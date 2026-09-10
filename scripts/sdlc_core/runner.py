"""Phase execution, evidence gates, synthesis, and bounded repair."""

from __future__ import annotations

import datetime as dt
import json
import os
import shlex
import subprocess
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Any

from .artifacts import list_value, parse_front_matter, validate_artifact
from .config import ALLOWED_TRANSITIONS, MAX_FIX_ATTEMPTS_PER_FINDING, MAX_TOTAL_FIX_ATTEMPTS, PHASE_ARTIFACTS
from .prompts import prompt_for, sibling_artifact
from .providers import adapter_command, load_profile
from .routing import apply_route_directives
from .schemas import validate_route
from .storage import utc_now, write_json, write_text
from .telemetry import record


def save_route(path: Path, route: dict[str, Any]) -> None:
    validate_route(route)
    write_json(path, route, backup=True)


def transition(route_path: Path, route: dict[str, Any], phase: str, status: str, **details: Any) -> None:
    state, previous = route["phase_states"][phase], route["phase_states"][phase]["status"]
    if status not in ALLOWED_TRANSITIONS.get(previous, set()):
        raise ValueError(f"invalid phase transition for {phase}: {previous} -> {status}")
    now = utc_now()
    state["status"] = status
    if status == "running":
        state["attempts"] += 1
        state["started_at"] = now
    if status in {"succeeded", "failed", "blocked", "needs-approval", "skipped"}:
        state["finished_at"] = now
    state.update(details)
    route["current_phase"] = phase
    route["status"] = {"running": "running", "succeeded": "phase-completed", "failed": "blocked", "blocked": "blocked", "needs-approval": "needs-approval", "skipped": "phase-completed"}.get(status, route["status"])
    route.setdefault("events", []).append({"event": f"phase-{status}", "phase": phase, "from": previous, "at": now, **details})
    save_route(route_path, route)


def execute_adapter(task_dir: Path, workspace: Path, phase: str, model: str, lane: str = "primary", output_artifact: str | None = None) -> int:
    profile, template = load_profile(model), adapter_command(model)
    if not template:
        print(f"No adapter configured for {model!r}. Set {profile['command_env']} or omit --execute.", file=os.sys.stderr)
        return 2
    if lane == "secondary" and not profile["capabilities"].get("parallel_processes"):
        print(f"Provider {model!r} does not declare parallel_processes capability.", file=os.sys.stderr)
        return 2
    suffix = "" if lane == "primary" else f"-{lane}"
    prompt_file = task_dir / f"prompt-{phase}{suffix}.md"
    write_text(prompt_file, prompt_for(task_dir, workspace, phase, model, lane, output_artifact))
    sidecar = f"adapter-{phase}{suffix}.telemetry.json"
    replacements = {
        "prompt_file": str(prompt_file), "workspace": str(workspace), "output_dir": str(task_dir),
        "task_id": task_dir.name, "output_artifact": output_artifact or PHASE_ARTIFACTS.get(phase, f"{phase}.md"),
        "telemetry_file": str(task_dir / sidecar),
    }
    started = time.monotonic()
    try:
        argv = shlex.split(template.format(**replacements), posix=os.name != "nt")
        if not argv:
            raise ValueError("adapter command is empty")
        completed = subprocess.run(argv, cwd=workspace, capture_output=True, text=True, check=False)
        result, stdout, stderr = completed.returncode, completed.stdout, completed.stderr
    except (OSError, ValueError) as exc:
        result, stdout, stderr = 2, "", str(exc)
    duration = int((time.monotonic() - started) * 1000)
    write_text(task_dir / f"adapter-{phase}{suffix}.stdout.txt", stdout)
    write_text(task_dir / f"adapter-{phase}{suffix}.stderr.txt", stderr)
    return result


def _record_call(task_dir: Path, route: dict[str, Any], phase: str, lane: str, model: str, result: int, duration_ms: int) -> None:
    suffix = "" if lane == "primary" else f"-{lane}"
    record(task_dir, route, {
        "phase": phase, "lane": lane, "model": model, "exit_code": result,
        "duration_ms": duration_ms, "telemetry_sidecar": f"adapter-{phase}{suffix}.telemetry.json",
    })


def run_synthesis(task_dir: Path, workspace: Path, route: dict[str, Any], source_phase: str, model: str, primary: str, secondary: str) -> tuple[int, str | None]:
    route_path, artifact = task_dir / "route.json", sibling_artifact(primary, "synthesis")
    lane = route["phase_states"][source_phase]["lanes"].setdefault("synthesis", {"status": "running"})
    save_route(route_path, route)
    started = time.monotonic()
    result = execute_adapter(task_dir, workspace, "synthesis", model, source_phase, artifact)
    _record_call(task_dir, route, "synthesis", source_phase, model, result, int((time.monotonic() - started) * 1000))
    lane.update({"status": "succeeded" if result == 0 else "failed", "exit_code": result, "artifact": artifact, "inputs": [primary, secondary]})
    if result:
        save_route(route_path, route)
        return result, None
    try:
        metadata = validate_artifact(task_dir / artifact, task_dir.name, "synthesis")
        if source_phase == "review" and metadata.get("decision") not in {"approve", "fix", "needs-review"}:
            raise ValueError("review synthesis requires a decision")
    except (OSError, ValueError) as exc:
        lane.update({"status": "failed", "error": str(exc)})
        save_route(route_path, route)
        return 3, None
    route["phase_states"][source_phase]["last_synthesis_artifact"] = artifact
    save_route(route_path, route)
    return 0, artifact


def run_phase(task_dir: Path, workspace: Path, route: dict[str, Any], phase: str, model: str, parallel_checks: bool = False, output_artifact: str | None = None) -> int:
    route_path = task_dir / "route.json"
    if phase not in route["phase_states"]:
        route["phase_states"][phase] = {"status": "pending", "attempts": 0, "lanes": {"primary": {"status": "pending"}}}
        save_route(route_path, route)
    transition(route_path, route, phase, "running")
    primary = output_artifact or PHASE_ARTIFACTS[phase]
    lanes = [("primary", primary)]
    if parallel_checks and phase in {"audit", "review"}:
        lanes.append(("secondary", sibling_artifact(primary, "secondary")))
    state = route["phase_states"][phase]
    for lane, _ in lanes:
        state["lanes"].setdefault(lane, {})["status"] = "running"
    save_route(route_path, route)

    def invoke(lane: str, artifact: str) -> tuple[int, int]:
        started = time.monotonic()
        result = execute_adapter(task_dir, workspace, phase, model, lane, artifact)
        return result, int((time.monotonic() - started) * 1000)

    if len(lanes) == 1:
        results = [invoke(*lanes[0])]
    else:
        with ThreadPoolExecutor(max_workers=2) as pool:
            results = [future.result() for future in [pool.submit(invoke, *lane) for lane in lanes]]
    for (lane, artifact), (result, duration) in zip(lanes, results):
        state["lanes"][lane].update({"status": "succeeded" if result == 0 else "failed", "exit_code": result, "artifact": artifact})
        _record_call(task_dir, route, phase, lane, model, result, duration)
    if any(result for result, _ in results):
        save_route(route_path, route)
        transition(route_path, route, phase, "blocked", reason="adapter failure")
        return next(result for result, _ in results if result)
    try:
        metadata = {artifact: validate_artifact(task_dir / artifact, task_dir.name, phase) for _, artifact in lanes}
    except (OSError, ValueError) as exc:
        save_route(route_path, route)
        transition(route_path, route, phase, "blocked", reason=f"invalid required artifact: {exc}")
        return 3
    if any(item["status"] == "blocked" for item in metadata.values()):
        transition(route_path, route, phase, "blocked", reason="phase artifact reports blocked")
        return 3
    if any(item["status"] == "needs-review" for item in metadata.values()):
        transition(route_path, route, phase, "needs-approval", reason="phase artifact requires human review")
        return 4
    apply_route_directives(route, metadata[primary], phase)
    if len(lanes) == 2:
        result, synthesis = run_synthesis(task_dir, workspace, route, phase, model, primary, lanes[1][1])
        if result:
            transition(route_path, route, phase, "blocked", reason="parallel evidence synthesis failed")
            return result
        state["last_synthesis_artifact"] = synthesis
    state["last_artifact"] = primary
    transition(route_path, route, phase, "succeeded", artifacts=[artifact for _, artifact in lanes])
    route.setdefault("completed_phases", []).append(phase)
    save_route(route_path, route)
    return 0


def review_decision(task_dir: Path, route: dict[str, Any]) -> tuple[str, list[str]]:
    state = route["phase_states"]["review"]
    artifact = state.get("last_synthesis_artifact") or state.get("last_artifact", "review.md")
    metadata = parse_front_matter(task_dir / artifact)
    return metadata.get("decision", "needs-review"), list_value(metadata.get("blocking_findings"))


def run_review_fix_loop(task_dir: Path, workspace: Path, route: dict[str, Any], model: str, parallel_checks: bool) -> int:
    route_path = task_dir / "route.json"
    while True:
        decision, findings = review_decision(task_dir, route)
        if decision == "approve":
            return 0
        if decision != "fix" or not findings:
            route.update({"status": "needs-review", "blocked_reason": "review requires a human decision or stable blocking findings"})
            save_route(route_path, route)
            return 4
        history, total = route.setdefault("finding_attempts", {}), route.get("fix_attempts", 0)
        exhausted = [finding for finding in findings if history.get(finding, 0) >= MAX_FIX_ATTEMPTS_PER_FINDING]
        if exhausted or total >= MAX_TOTAL_FIX_ATTEMPTS:
            route.update({"status": "needs-review", "blocked_reason": f"fix limit reached for: {', '.join(exhausted) or 'cycle'}"})
            route.setdefault("events", []).append({"event": "fix-limit-reached", "findings": exhausted, "at": utc_now(), "reason": "bounded repair budget exhausted"})
            save_route(route_path, route)
            return 4
        attempt = total + 1
        route["fix_attempts"] = attempt
        for finding in findings:
            history[finding] = history.get(finding, 0) + 1
        route.setdefault("fix_history", []).append({"attempt": attempt, "findings": findings, "at": utc_now()})
        save_route(route_path, route)
        for current, artifact in (("fix", f"fix-report-{attempt}.md"), ("test", f"test-report-{attempt}.md"), ("review", f"review-{attempt}.md")):
            result = run_phase(task_dir, workspace, route, current, model, parallel_checks if current == "review" else False, artifact)
            if result:
                return result


def run_full_cycle(task_dir: Path, workspace: Path, route: dict[str, Any], model: str, parallel_checks: bool = False) -> int:
    route_path = task_dir / "route.json"
    index = 0
    while index < len(route["phases"]):
        phase = route["phases"][index]
        if route["phase_states"][phase]["status"] in {"succeeded", "skipped"}:
            index += 1
            continue
        if phase == "approval":
            transition(route_path, route, phase, "needs-approval")
            print("Autopilot paused at the human approval gate.")
            return 0
        result = run_phase(task_dir, workspace, route, phase, model, parallel_checks)
        if result:
            return 0 if result == 4 else result
        if phase == "review":
            result = run_review_fix_loop(task_dir, workspace, route, model, parallel_checks)
            if result:
                return 0 if result == 4 else result
        index += 1
    route.update({"status": "completed", "current_phase": route["phases"][-1], "completed_at": utc_now()})
    save_route(route_path, route)
    print("Autopilot completed the routed SDLC cycle.")
    return 0
