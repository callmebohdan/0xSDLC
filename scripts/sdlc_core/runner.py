"""Phase execution, evidence gates, synthesis, and bounded repair."""

from __future__ import annotations

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
from .telemetry import close_attempt, elapsed_ms, open_attempt, persist_result, prepare_call, start_call, sync_metrics


def save_route(path: Path, route: dict[str, Any]) -> None:
    validate_route(route)
    write_json(path, route, backup=True)


def transition(route_path: Path, route: dict[str, Any], phase: str, status: str, *, persist: bool = True, **details: Any) -> None:
    state, previous = route["phase_states"][phase], route["phase_states"][phase]["status"]
    if status not in ALLOWED_TRANSITIONS.get(previous, set()):
        raise ValueError(f"invalid phase transition for {phase}: {previous} -> {status}")
    now = details.get("started_at") or details.get("finished_at") or utc_now()
    state["status"] = status
    if status == "running":
        state["attempts"] += 1
        state["started_at"] = now
        state["finished_at"] = None
        state.pop("reason", None)
    if status in {"succeeded", "failed", "blocked", "needs-approval", "needs-review", "skipped"}:
        state["finished_at"] = now
    state.update(details)
    route["current_phase"] = phase
    route["status"] = {"running": "running", "succeeded": "phase-completed", "failed": "blocked", "blocked": "blocked", "needs-approval": "needs-approval", "needs-review": "needs-review", "skipped": "phase-completed"}.get(status, route["status"])
    route.setdefault("events", []).append({"event": f"phase-{status}", "phase": phase, "from": previous, "at": now, **details})
    if persist:
        save_route(route_path, route)


def execute_adapter(
    task_dir: Path,
    workspace: Path,
    phase: str,
    model: str,
    event: dict[str, Any],
    evidence_inputs: list[str] | None = None,
) -> int:
    lane, evidence = event["lane"], event["evidence"]
    profile, template = load_profile(model), adapter_command(model)
    prompt_file = task_dir / evidence["prompt"]
    write_text(prompt_file, prompt_for(task_dir, workspace, phase, model, lane, evidence["artifact"], evidence_inputs))
    replacements = {
        "prompt_file": str(prompt_file), "workspace": str(workspace), "output_dir": str(task_dir),
        "task_id": task_dir.name, "output_artifact": evidence["artifact"],
        "telemetry_file": str(task_dir / event["telemetry_sidecar"]), "call_id": event["call_id"],
    }
    start_call(task_dir, event, profile["name"])
    started = time.monotonic()
    try:
        if not template:
            raise ValueError(f"No adapter configured for {model!r}. Set {profile['command_env']} or omit --execute.")
        if lane in {"secondary", "maintainability"} and not profile["capabilities"].get("parallel_processes"):
            raise ValueError(f"Provider {model!r} does not declare parallel_processes capability.")
        command = template.format(**replacements).strip()
        argv = command if os.name == "nt" else shlex.split(command)
        if not argv:
            raise ValueError("adapter command is empty")
        completed = subprocess.run(
            argv, cwd=workspace, capture_output=True, text=True, errors="replace", check=False,
            env={**os.environ, "0XSDLC_CALL_ID": event["call_id"]},
        )
        result, stdout, stderr = completed.returncode, completed.stdout, completed.stderr
    except (OSError, ValueError, KeyError) as exc:
        result, stdout, stderr = 2, "", str(exc)
        print(stderr, file=os.sys.stderr)
    event.update(
        finished_at=utc_now(), duration_ms=elapsed_ms(started), exit_code=result,
        outcome="succeeded" if result == 0 else "failed",
    )
    write_text(task_dir / evidence["stdout"], stdout)
    write_text(task_dir / evidence["stderr"], stderr)
    persist_result(task_dir, event)
    return result


def start_attempt(task_dir: Path, workspace: Path, route: dict[str, Any], phase: str) -> dict[str, Any]:
    state = route["phase_states"][phase]
    if "running" not in ALLOWED_TRANSITIONS.get(state["status"], set()):
        raise ValueError(f"cannot open phase {phase}: {state['status']}")
    attempt = open_attempt(workspace, route.get("execution", "adapter"), route["model"], utc_now())
    state.setdefault("attempt_history", []).append(attempt)
    state["lanes"] = {"primary": {"status": "pending"}}
    for field in ("last_artifact", "last_synthesis_artifact"):
        state.pop(field, None)
    transition(task_dir / "route.json", route, phase, "running", attempt_id=attempt["attempt_id"], started_at=attempt["started_at"])
    return attempt


def finish_attempt(task_dir: Path, workspace: Path, route: dict[str, Any], phase: str, status: str, *, persist: bool = True, **details: Any) -> None:
    state = route["phase_states"][phase]
    attempt = state["attempt_history"][-1]
    close_attempt(attempt, workspace, status, utc_now())
    sync_metrics(task_dir, route)
    transition(task_dir / "route.json", route, phase, status, persist=persist, finished_at=attempt["finished_at"], **details)


def reserve_artifact(task_dir: Path, state: dict[str, Any], preferred: str) -> str:
    *previous, current = state["attempt_history"]
    if (task_dir / preferred).exists() or any(preferred in attempt["artifacts"] for attempt in previous):
        preferred = sibling_artifact(preferred, f"attempt-{current['attempt_id']}")
    current["artifacts"].append(preferred)
    return preferred


def run_synthesis(
    task_dir: Path,
    workspace: Path,
    route: dict[str, Any],
    source_phase: str,
    model: str,
    evidence: list[str],
) -> tuple[int, str | None]:
    primary = evidence[0]
    route_path, state = task_dir / "route.json", route["phase_states"][source_phase]
    artifact = reserve_artifact(task_dir, state, sibling_artifact(primary, "synthesis"))
    event = prepare_call(task_dir, state["attempt_history"][-1], "synthesis", source_phase, model, artifact)
    lane = state["lanes"].setdefault("synthesis", {"status": "running", "call_id": event["call_id"]})
    save_route(route_path, route)
    result = execute_adapter(task_dir, workspace, "synthesis", model, event, evidence)
    sync_metrics(task_dir, route)
    lane.update({"status": "succeeded" if result == 0 else "failed", "exit_code": result, "artifact": artifact, "inputs": evidence})
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


def run_phase(
    task_dir: Path,
    workspace: Path,
    route: dict[str, Any],
    phase: str,
    model: str,
    parallel_checks: bool = False,
    output_artifact: str | None = None,
    maintainability_review: bool = False,
) -> int:
    route_path = task_dir / "route.json"
    if phase not in route["phase_states"]:
        route["phase_states"][phase] = {"status": "pending", "attempts": 0, "lanes": {"primary": {"status": "pending"}}}
        save_route(route_path, route)
    attempt = start_attempt(task_dir, workspace, route, phase)
    state = route["phase_states"][phase]
    requested = output_artifact or PHASE_ARTIFACTS[phase]
    lanes = [("primary", requested)]
    if parallel_checks and phase in {"audit", "review"}:
        lanes.append(("secondary", sibling_artifact(requested, "secondary")))
    if maintainability_review and phase == "review":
        lanes.append(("maintainability", sibling_artifact(requested, "maintainability")))
    lanes = [(lane, reserve_artifact(task_dir, state, artifact)) for lane, artifact in lanes]
    primary = lanes[0][1]
    events = [prepare_call(task_dir, attempt, phase, lane, model, artifact) for lane, artifact in lanes]
    for (lane, artifact), event in zip(lanes, events):
        state["lanes"][lane] = {"status": "running", "call_id": event["call_id"], "artifact": artifact}
    save_route(route_path, route)

    def invoke(event: dict[str, Any]) -> int:
        return execute_adapter(task_dir, workspace, phase, model, event)

    if len(lanes) == 1:
        results = [invoke(events[0])]
    else:
        with ThreadPoolExecutor(max_workers=len(lanes)) as pool:
            results = list(pool.map(invoke, events))
    for (lane, artifact), result in zip(lanes, results):
        state["lanes"][lane].update({"status": "succeeded" if result == 0 else "failed", "exit_code": result, "artifact": artifact})
    if any(results):
        finish_attempt(task_dir, workspace, route, phase, "failed", reason="adapter failure")
        return next(result for result in results if result)
    try:
        metadata = {artifact: validate_artifact(task_dir / artifact, task_dir.name, phase) for _, artifact in lanes}
    except (OSError, ValueError) as exc:
        finish_attempt(task_dir, workspace, route, phase, "blocked", reason=f"invalid required artifact: {exc}")
        return 3
    state["last_artifact"] = primary
    if any(item["status"] == "blocked" for item in metadata.values()):
        finish_attempt(task_dir, workspace, route, phase, "blocked", reason="phase artifact reports blocked")
        return 3
    if any(item["status"] == "needs-review" for item in metadata.values()):
        finish_attempt(task_dir, workspace, route, phase, "needs-review", reason="phase artifact requires human review")
        return 4
    apply_route_directives(route, metadata[primary], phase)
    if len(lanes) > 1:
        result, synthesis = run_synthesis(task_dir, workspace, route, phase, model, [artifact for _, artifact in lanes])
        if result:
            finish_attempt(task_dir, workspace, route, phase, "blocked", reason="parallel evidence synthesis failed")
            return result
        state["last_synthesis_artifact"] = synthesis
    state["last_artifact"] = primary
    route.setdefault("completed_phases", []).append(phase)
    finish_attempt(task_dir, workspace, route, phase, "succeeded", artifacts=[artifact for _, artifact in lanes])
    return 0


def review_decision(task_dir: Path, route: dict[str, Any]) -> tuple[str, list[str]]:
    state = route["phase_states"]["review"]
    artifact = state.get("last_synthesis_artifact") or state.get("last_artifact", "review.md")
    metadata = parse_front_matter(task_dir / artifact)
    return metadata.get("decision", "needs-review"), list_value(metadata.get("blocking_findings"))


def test_decision(task_dir: Path, route: dict[str, Any]) -> tuple[str, list[str]]:
    state = route["phase_states"]["test"]
    artifact = state.get("last_artifact", "test-report.md")
    metadata = parse_front_matter(task_dir / artifact)
    outcome = metadata.get("test_outcome")
    if outcome == "pass":
        return "approve", []
    if outcome == "fail":
        return "fix", list_value(metadata.get("blocking_findings"))
    return "needs-review", list_value(metadata.get("blocking_findings"))


def run_fix_loop(
    task_dir: Path,
    workspace: Path,
    route: dict[str, Any],
    model: str,
    parallel_checks: bool,
    maintainability_review: bool,
    source_phase: str = "review",
) -> int:
    route_path = task_dir / "route.json"
    while True:
        active = route.get("active_repair")
        if active:
            phase = active["phase"]
            state = route["phase_states"].get(phase, {})
            if state.get("status") != "succeeded" or state["attempts"] <= active["previous_attempts"]:
                artifact = sibling_artifact(PHASE_ARTIFACTS[phase], str(active["number"]))
                result = run_phase(task_dir, workspace, route, phase, model, parallel_checks, artifact, maintainability_review)
                if result:
                    return result
            next_phase = {"fix": "test", "test": "review"}.get(phase)
            if phase == "test" and test_decision(task_dir, route)[0] != "approve":
                next_phase = None
            if next_phase:
                active.update(phase=next_phase, previous_attempts=route["phase_states"].get(next_phase, {}).get("attempts", 0))
            else:
                source_phase = phase
                del route["active_repair"]
            save_route(route_path, route)
            continue
        decision, findings = test_decision(task_dir, route) if source_phase == "test" else review_decision(task_dir, route)
        if decision == "approve":
            return 0
        if decision != "fix" or not findings:
            route.update({"status": "needs-review", "blocked_reason": f"{source_phase} requires a human decision or stable blocking finding IDs"})
            save_route(route_path, route)
            return 4
        if route.get("mode", "change") != "change":
            route.update({"status": "needs-review", "blocked_reason": "read-only route found a product issue; implementation is not permitted"})
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
        route.setdefault("events", []).append({
            "event": "repair-loop-started", "source_phase": source_phase, "attempt": attempt,
            "findings": findings, "at": utc_now(),
            "reason": f"{source_phase} reported stable blocking findings",
        })
        route["active_repair"] = {
            "number": attempt, "phase": "fix", "previous_attempts": route["phase_states"].get("fix", {}).get("attempts", 0),
        }
        save_route(route_path, route)


def run_full_cycle(
    task_dir: Path,
    workspace: Path,
    route: dict[str, Any],
    model: str,
    parallel_checks: bool = False,
    maintainability_review: bool = False,
) -> int:
    route_path = task_dir / "route.json"
    if route["status"] == "completed":
        print("Autopilot cycle is already completed.")
        return 0
    if route.get("active_repair"):
        result = run_fix_loop(task_dir, workspace, route, model, parallel_checks, maintainability_review)
        if result:
            return 0 if result == 4 else result
    index = 0
    while index < len(route["phases"]):
        phase = route["phases"][index]
        state = route["phase_states"][phase]
        status = state["status"]
        if status == "skipped" or (status == "succeeded" and not state.get("attempt_history")):
            index += 1
            continue
        if status != "succeeded":
            if phase == "approval":
                transition(route_path, route, phase, "needs-approval")
                print("Autopilot paused at the human approval gate.")
                return 0
            result = run_phase(task_dir, workspace, route, phase, model, parallel_checks, maintainability_review=maintainability_review)
            if result:
                return 0 if result == 4 else result
        if phase == "test":
            decision, _ = test_decision(task_dir, route)
            if decision != "approve":
                result = run_fix_loop(task_dir, workspace, route, model, parallel_checks, maintainability_review, "test")
                if result:
                    return 0 if result == 4 else result
        if phase == "review":
            result = run_fix_loop(task_dir, workspace, route, model, parallel_checks, maintainability_review)
            if result:
                return 0 if result == 4 else result
        index += 1
    route.update({"status": "completed", "current_phase": route["phases"][-1], "completed_at": utc_now()})
    save_route(route_path, route)
    print("Autopilot completed the routed SDLC cycle.")
    return 0
