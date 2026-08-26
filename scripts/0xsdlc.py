"""Small, model-neutral orchestration CLI for 0xSDLC.

The CLI owns task folders and prompt packets. Provider-specific CLIs remain
optional and are invoked only with --execute and an explicit environment
configuration.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import re
import shlex
import subprocess
import sys
import uuid
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]

PHASE_CONTRACTS = {
    "specify": "support/0xSDLC-spec/specification.md",
    "audit": "support/0xSDLC-audit/audit.md",
    "design": "0xSDLC-design/design.md",
    "plan": "0xSDLC-plan/planning.md",
    "implement": "0xSDLC-implement/implementation.md",
    "test": "support/0xSDLC-test/testing.md",
    "review": "support/0xSDLC-review/review.md",
    "verify": "0xSDLC-verify/verification.md",
}


def default_system_agents() -> Path:
    """Return the user-level contract directory for the current OS."""
    override = os.environ.get("0XSDLC_AGENTS_HOME")
    if override:
        return Path(override).expanduser()
    if os.name == "nt":
        user_root = Path(os.environ.get("USERPROFILE", str(Path.home())))
        return user_root / ".agents" / "0xsdlc"
    return Path.home() / ".agents" / "0xsdlc"


SYSTEM_LIBRARY = default_system_agents()
LIBRARY = SYSTEM_LIBRARY if (SYSTEM_LIBRARY / "templates").exists() else ROOT
# Runtime evidence is user-level state, not repository content. On Windows this
# resolves to %USERPROFILE%\\.agents\\0xsdlc\\sessions.
TASKS = SYSTEM_LIBRARY / "sessions"

PHASE_ARTIFACTS = {
    "specify": "spec.md",
    "audit": "audit.md",
    "design": "design.md",
    "plan": "plan.md",
    "implement": "implementation.md",
    "test": "test-report.md",
    "review": "review.md",
    "verify": "verification.md",
    "fix": "fix-report.md",
}

PHASES = {
    "small": ["audit", "plan", "implement", "test", "review", "verify"],
    "standard": [
        "specify",
        "audit",
        "design",
        "plan",
        "implement",
        "test",
        "review",
        "verify",
    ],
    "high-risk": [
        "specify",
        "audit",
        "design",
        "plan",
        "approval",
        "implement",
        "test",
        "review",
        "verify",
    ],
}

PHASE_AGENT = {
    "specify": "specifier",
    "audit": "auditor",
    "design": "architect",
    "plan": "task-planner",
    "implement": "implementer",
    "test": "tester",
    "review": "reviewer",
    "verify": "verifier",
    "fix": "fixer",
}


def slugify(value: str) -> str:
    value = re.sub(r"[^a-zA-Z0-9]+", "-", value.lower()).strip("-")
    return value[:42] or "task"


def classify(request: str) -> str:
    high_risk = re.compile(
        r"\b(auth|authentication|authorization|security|secret|credential|password|"
        r"migration|database|deploy|deployment|production|billing|payment|public api|delete)\b",
        re.I,
    )
    if high_risk.search(request):
        return "high-risk"
    if len(request.split()) <= 14 and re.search(
        r"\b(fix|rename|typo|format|small|add test|update readme)\b", request, re.I
    ):
        return "small"
    return "standard"


def now_id(request: str) -> str:
    stamp = dt.datetime.now().strftime("%Y-%m-%d")
    return f"{stamp}_{slugify(request)}_{uuid.uuid4().hex[:8]}"


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content.rstrip() + "\n", encoding="utf-8")


def render_template(path: Path, values: dict[str, str]) -> str:
    content = path.read_text(encoding="utf-8")
    for key, value in values.items():
        content = content.replace("{{" + key + "}}", value)
    return content


def select_model(requested: str) -> str:
    if requested != "auto":
        return requested
    for name in ("codex", "claude", "generic"):
        if os.environ.get(f"0XSDLC_{name.upper()}_COMMAND"):
            return name
    return "generic"


def adapter_command(model: str) -> str | None:
    return os.environ.get(f"0XSDLC_{model.upper()}_COMMAND")


def route_payload(task_id: str, request: str, kind: str, model: str) -> dict[str, Any]:
    phases = PHASES[kind]
    return {
        "schema_version": "0.2",
        "task_id": task_id,
        "request": request,
        "classification": kind,
        "model": model,
        "status": "prepared",
        "current_phase": phases[0],
        "phases": phases,
        "human_gates": ["approval"] if "approval" in phases else [],
        "phase_states": {
            phase: {"status": "pending", "attempts": 0, "lanes": {"primary": {"status": "pending"}}}
            for phase in phases
        },
        "events": [{"event": "route-prepared", "at": dt.datetime.now(dt.timezone.utc).isoformat()}],
        "created_at": dt.datetime.now(dt.timezone.utc).isoformat(),
    }


ALLOWED_TRANSITIONS = {
    "pending": {"running", "needs-approval", "skipped"},
    "running": {"succeeded", "failed", "blocked", "needs-approval"},
    "succeeded": {"running"},
    "failed": {"running", "blocked"},
    "blocked": {"running"},
    "needs-approval": {"running"},
    "skipped": set(),
}


def save_route(route_path: Path, route: dict[str, Any]) -> None:
    write_text(route_path, json.dumps(route, indent=2))


def transition(route_path: Path, route: dict[str, Any], phase: str, status: str, **details: Any) -> None:
    state = route["phase_states"][phase]
    previous = state["status"]
    if status not in ALLOWED_TRANSITIONS.get(previous, set()):
        raise ValueError(f"invalid phase transition for {phase}: {previous} -> {status}")
    now = dt.datetime.now(dt.timezone.utc).isoformat()
    state["status"] = status
    if status == "running":
        state["attempts"] += 1
        state["started_at"] = now
    if status in {"succeeded", "failed", "blocked", "needs-approval", "skipped"}:
        state["finished_at"] = now
    state.update(details)
    route["current_phase"] = phase
    route["status"] = {
        "running": "running",
        "succeeded": "phase-completed",
        "failed": "blocked",
        "blocked": "blocked",
        "needs-approval": "needs-approval",
        "skipped": "phase-completed",
    }.get(status, route["status"])
    route.setdefault("events", []).append(
        {"event": f"phase-{status}", "phase": phase, "from": previous, "at": now, **details}
    )
    save_route(route_path, route)


def prompt_for(task_dir: Path, phase: str, model: str, lane: str = "primary", output_artifact: str | None = None) -> str:
    task_id = task_dir.name
    agent = PHASE_AGENT.get(phase, "orchestrator")
    contract_relative = PHASE_CONTRACTS.get(phase)
    contract = LIBRARY / contract_relative if contract_relative else LIBRARY / "support" / "adapters" / "generic.md"
    if not contract.is_file():
        contract = LIBRARY / "support" / "adapters" / "generic.md"
    route = json.loads((task_dir / "route.json").read_text(encoding="utf-8"))
    artifact_names = [p.name for p in task_dir.iterdir() if p.is_file()]
    return f"""# 0xSDLC phase packet

Task ID: `{task_id}`
Model adapter: `{model}`
Phase: `{phase}`
Agent: `{agent}`
Workspace: `{ROOT}`

## Mission

Perform only the `{phase}` phase for task `{task_id}` in the `{lane}` lane. Follow the phase contract below and write the named output artifact into `{task_dir}`. Do not claim work that was not performed.

Required output artifact: `{output_artifact or PHASE_ARTIFACTS.get(phase, f'{phase}.md')}`

## Route

```json
{json.dumps(route, indent=2)}
```

## Available task artifacts

{os.linesep.join(f"- `{name}`" for name in sorted(artifact_names))}

## Phase contract

{contract.read_text(encoding="utf-8")}

## Global boundaries

{(LIBRARY / "support" / "0xSDLC-conventions" / "boundaries.md").read_text(encoding="utf-8")}

## Output requirement

Return a concise summary, status, evidence, assumptions, and unresolved risks. Keep all durable handoff information in the task artifact, not only in chat.
"""


def execute_adapter(
    task_dir: Path,
    phase: str,
    model: str,
    lane: str = "primary",
    output_artifact: str | None = None,
) -> int:
    template = adapter_command(model)
    if not template:
        print(
            f"No adapter configured for {model!r}. Set 0XSDLC_{model.upper()}_COMMAND or omit --execute.",
            file=sys.stderr,
        )
        return 2
    suffix = "" if lane == "primary" else f"-{lane}"
    prompt_file = task_dir / f"prompt-{phase}{suffix}.md"
    write_text(prompt_file, prompt_for(task_dir, phase, model, lane, output_artifact))
    replacements = {
        "prompt_file": str(prompt_file),
        "workspace": str(ROOT),
        "output_dir": str(task_dir),
        "task_id": task_dir.name,
    }
    try:
        command = template.format(**replacements)
        argv = shlex.split(command, posix=os.name != "nt")
        if not argv:
            raise ValueError("adapter command is empty")
        completed = subprocess.run(
            argv,
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
    except (OSError, ValueError) as exc:
        write_text(task_dir / "adapter-error.txt", str(exc))
        print(f"Adapter could not start: {exc}", file=sys.stderr)
        return 2
    write_text(task_dir / f"adapter-{phase}{suffix}.stdout.txt", completed.stdout)
    write_text(task_dir / f"adapter-{phase}{suffix}.stderr.txt", completed.stderr)
    return completed.returncode


def review_decision(task_dir: Path, parallel_checks: bool = False) -> str:
    """Read the review's explicit decision; conservative fallback treats clear findings as fixes."""
    reports = [task_dir / "review.md"]
    if parallel_checks:
        reports.append(task_dir / "review-secondary.md")
    decisions: list[str] = []
    for report in reports:
        if not report.is_file():
            continue
        text = report.read_text(encoding="utf-8")
        match = re.search(r"^decision:\s*[\"']?(approve|fix|needs-review)[\"']?\s*$", text, re.I | re.M)
        if match:
            decisions.append(match.group(1).lower())
        elif re.search(r"return for fixes|open finding|P[01].*(?:open|unresolved|block)", text, re.I):
            decisions.append("fix")
        else:
            decisions.append("needs-review")
    if "fix" in decisions:
        return "fix"
    if "needs-review" in decisions:
        return "needs-review"
    return "approve"


def run_phase(
    task_dir: Path,
    route: dict[str, Any],
    phase: str,
    model: str,
    parallel_checks: bool = False,
    output_artifact: str | None = None,
) -> int:
    """Execute one phase and enforce its state and artifact contract."""
    route_path = task_dir / "route.json"
    if phase not in route["phase_states"]:
        route["phase_states"][phase] = {"status": "pending", "attempts": 0, "lanes": {"primary": {"status": "pending"}}}
        save_route(route_path, route)
    transition(route_path, route, phase, "running")
    lanes = [("primary", output_artifact or PHASE_ARTIFACTS.get(phase))]
    if parallel_checks and phase in {"audit", "review"}:
        lanes.append(("secondary", f"{phase}-secondary.md"))
        route["phase_states"][phase]["lanes"]["secondary"] = {"status": "running"}
        save_route(route_path, route)
    route["phase_states"][phase]["lanes"]["primary"]["status"] = "running"
    if len(lanes) == 1:
        results = [execute_adapter(task_dir, phase, model, lanes[0][0], lanes[0][1])]
    else:
        from concurrent.futures import ThreadPoolExecutor

        with ThreadPoolExecutor(max_workers=2) as pool:
            futures = [pool.submit(execute_adapter, task_dir, phase, model, lane, artifact) for lane, artifact in lanes]
            results = [future.result() for future in futures]
    for (lane, _), result in zip(lanes, results):
        route["phase_states"][phase]["lanes"][lane].update({"status": "succeeded" if result == 0 else "failed", "exit_code": result})
    save_route(route_path, route)
    if any(result != 0 for result in results):
        transition(route_path, route, phase, "blocked", reason="adapter failure")
        return next(result for result in results if result != 0)
    missing = [artifact for _, artifact in lanes if artifact and not (task_dir / artifact).is_file()]
    if missing:
        transition(route_path, route, phase, "blocked", reason=f"missing required artifact(s): {', '.join(missing)}")
        print(f"Autopilot stopped; missing artifact(s): {', '.join(missing)}", file=sys.stderr)
        return 3
    transition(route_path, route, phase, "succeeded", artifacts=[artifact for _, artifact in lanes if artifact])
    route.setdefault("completed_phases", []).append(phase)
    save_route(route_path, route)
    return 0


def run_full_cycle(task_dir: Path, route: dict[str, Any], model: str, parallel_checks: bool = False) -> int:
    """Run the route and bounded fix loop, stopping at gates, failures, or missing proof."""
    route_path = task_dir / "route.json"
    index = 0
    while index < len(route["phases"]):
        phase = route["phases"][index]
        if phase == "approval":
            transition(route_path, route, phase, "needs-approval")
            print("Autopilot paused at the human approval gate.")
            return 0
        result = run_phase(task_dir, route, phase, model, parallel_checks)
        if result:
            return result
        if phase == "review":
            fix_attempts = route.setdefault("fix_attempts", 0)
            while review_decision(task_dir, parallel_checks) == "fix":
                if fix_attempts >= 2:
                    route["status"] = "needs-review"
                    route["blocked_reason"] = "maximum fix attempts reached for review findings"
                    route.setdefault("events", []).append({"event": "fix-limit-reached", "phase": "review", "at": dt.datetime.now(dt.timezone.utc).isoformat()})
                    save_route(route_path, route)
                    return 3
                fix_attempts += 1
                route["fix_attempts"] = fix_attempts
                save_route(route_path, route)
                fix_artifact = f"fix-report-{fix_attempts}.md"
                result = run_phase(task_dir, route, "fix", model, output_artifact=fix_artifact)
                if result:
                    return result
                result = run_phase(task_dir, route, "test", model)
                if result:
                    return result
                result = run_phase(task_dir, route, "review", model, parallel_checks)
                if result:
                    return result
            if review_decision(task_dir, parallel_checks) == "needs-review":
                route["status"] = "needs-review"
                route.setdefault("events", []).append({"event": "review-needs-human", "at": dt.datetime.now(dt.timezone.utc).isoformat()})
                save_route(route_path, route)
                return 0
        index += 1
    route["status"] = "completed"
    route["current_phase"] = route["phases"][-1]
    save_route(route_path, route)
    print("Autopilot completed the routed SDLC cycle.")
    return 0


def cmd_autopilot(args: argparse.Namespace) -> int:
    TASKS.mkdir(parents=True, exist_ok=True)
    task_id = now_id(args.request)
    task_dir = TASKS / task_id
    task_dir.mkdir()
    model = select_model(args.model)
    kind = args.kind or classify(args.request)
    brief = render_template(
        LIBRARY / "templates" / "brief.md",
        {"task_id": task_id, "request": args.request},
    )
    write_text(task_dir / "brief.md", brief)
    route = route_payload(task_id, args.request, kind, model)
    write_text(task_dir / "route.json", json.dumps(route, indent=2))
    first_phase = route["current_phase"]
    if first_phase != "approval":
        write_text(task_dir / f"prompt-{first_phase}.md", prompt_for(task_dir, first_phase, model))
    print(f"Task: {task_id}")
    print(f"Classification: {kind}")
    print(f"Model adapter: {model}")
    print(f"Route: {' -> '.join(route['phases'])}")
    print(f"Artifacts: {task_dir}")
    if args.full and not args.execute:
        print("--full requires --execute so an adapter can run every phase.", file=sys.stderr)
        return 2
    if args.parallel_checks and not args.full:
        print("--parallel-checks requires --full so audit/review lanes have their prerequisites.", file=sys.stderr)
        return 2
    if args.full and first_phase != "approval":
        return run_full_cycle(task_dir, route, model, args.parallel_checks)
    if args.execute and first_phase != "approval":
        route_path = task_dir / "route.json"
        transition(route_path, route, first_phase, "running")
        result = execute_adapter(task_dir, first_phase, model, "primary", PHASE_ARTIFACTS.get(first_phase))
        if result != 0:
            transition(route_path, route, first_phase, "blocked", reason="adapter failure", exit_code=result)
            return result
        expected = PHASE_ARTIFACTS.get(first_phase)
        if expected and not (task_dir / expected).is_file():
            transition(route_path, route, first_phase, "blocked", reason=f"missing required artifact: {expected}")
            return 3
        transition(route_path, route, first_phase, "succeeded", artifacts=[expected] if expected else [])
        return 0
    if first_phase == "approval":
        print("Paused at the human approval gate before implementation.")
    else:
        print(f"Prepared prompt: {task_dir / f'prompt-{first_phase}.md'}")
    return 0


def cmd_status(_: argparse.Namespace) -> int:
    if not TASKS.exists():
        print("No 0xSDLC tasks yet.")
        return 0
    rows = []
    for route_path in sorted(TASKS.glob("*/route.json"), reverse=True):
        try:
            route = json.loads(route_path.read_text(encoding="utf-8"))
            rows.append(
                f"{route['task_id']} | {route['status']} | {route['classification']} | {route['current_phase']}"
            )
        except (OSError, json.JSONDecodeError, KeyError):
            rows.append(f"{route_path.parent.name} | invalid route.json")
    print("\n".join(rows) or "No 0xSDLC tasks yet.")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="0xsdlc", description="Lightweight spec-driven agent harness")
    sub = parser.add_subparsers(dest="command", required=True)
    autopilot = sub.add_parser("autopilot", help="route a task through the SDLC harness")
    autopilot.add_argument("request", help="short natural-language task")
    autopilot.add_argument("--model", default="auto", help="adapter name, e.g. codex, claude, qwen, generic")
    autopilot.add_argument("--kind", choices=sorted(PHASES), help="override automatic risk classification")
    autopilot.add_argument("--execute", action="store_true", help="invoke the configured adapter for the first phase")
    autopilot.add_argument("--full", action="store_true", help="with --execute, run the complete route until a gate, failure, or missing proof")
    autopilot.add_argument("--parallel-checks", action="store_true", help="with --full, run independent audit and review lanes; costs extra model calls")
    autopilot.set_defaults(func=cmd_autopilot)
    status = sub.add_parser("status", help="list generated task routes")
    status.set_defaults(func=cmd_status)
    return parser


if __name__ == "__main__":
    parsed = build_parser().parse_args()
    raise SystemExit(parsed.func(parsed))
