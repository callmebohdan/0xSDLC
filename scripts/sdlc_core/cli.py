"""Command-line interface for 0xSDLC."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import sys
import uuid
from pathlib import Path
from typing import Any

from .config import (
    ALLOWED_TRANSITIONS,
    BASE_PHASES,
    PHASE_ARTIFACTS,
    ROUTE_SCHEMA_VERSION,
    library_path,
    session_roots,
    sessions_root,
)
from .native import close_phase, interrupt_phase, open_phase
from .project import agents_draft, current_git_branch, project_profile
from .prompts import prompt_for
from .providers import select_model, validate_profiles
from .routing import classify, infer_mode, migrate_route, needs_design, route_payload
from .runner import run_full_cycle, run_phase, save_route, transition
from .schemas import validate_route
from .storage import TaskLock, check_session_writable, read_json, recover_interrupted, utc_now, write_json, write_text
from .telemetry import summarize, sync_metrics


def slugify(value: str) -> str:
    return re.sub(r"[^a-zA-Z0-9]+", "-", value.lower()).strip("-")[:42] or "task"


def now_id(request: str) -> str:
    return f"{dt.datetime.now().strftime('%Y-%m-%d')}_{slugify(request)}_{uuid.uuid4().hex[:8]}"


def render_template(path: Path, values: dict[str, str]) -> str:
    content = path.read_text(encoding="utf-8")
    for key, value in values.items():
        content = content.replace("{{" + key + "}}", value)
    return content


def create_task(args: argparse.Namespace) -> tuple[Path, Path, dict[str, Any], str]:
    workspace = args.workspace.expanduser().resolve()
    if not workspace.is_dir():
        raise ValueError(f"workspace is not a directory: {workspace}")
    tasks = sessions_root(args.sessions_root, workspace)
    check_session_writable(tasks)
    task_id = now_id(args.request)
    task_dir = tasks / task_id
    task_dir.mkdir()
    if args.native:
        model = "native" if args.model == "auto" else args.model
    else:
        model = select_model(args.model)
    kind = args.kind or classify(args.request)
    mode = infer_mode(args.request, args.mode)
    include_design = True if kind == "high-risk" else (args.design if args.design is not None else needs_design(args.request, kind))
    route = route_payload(
        task_id,
        args.request,
        kind,
        model,
        include_design,
        args.approval or kind == "high-risk",
        str(workspace),
        args.maintainability_review,
        mode,
        args.quality_control,
    )
    route["git_branch"] = current_git_branch(workspace)
    if args.native:
        route["execution"] = "native"
    if args.parallel_checks:
        route["routing"]["parallel_checks"] = True
    if args.phase:
        route.update(phases=[args.phase], current_phase=args.phase, standalone_phase=True, human_gates=[])
        route["phase_states"] = {args.phase: {"status": "pending", "attempts": 0, "lanes": {"primary": {"status": "pending"}}}}
        route["routing"].update(design=args.phase == "design", approval=False, quality_control=args.phase == "quality-control")
    if args.maintainability_review:
        route["events"].append({
            "event": "review-lane-selected",
            "at": utc_now(),
            "reason": "human requested focused maintainability review",
        })
    write_text(task_dir / "brief.md", render_template(library_path("templates/brief.md"), {"task_id": task_id, "request": args.request, "mode": mode}))
    profile = project_profile(workspace)
    write_json(task_dir / "project-profile.json", profile)
    if not (workspace / "AGENTS.md").is_file():
        write_text(task_dir / "project-context.md", agents_draft(profile))
        route["events"].append({"event": "project-instructions-missing", "at": utc_now(), "reason": "using task-local project context; run bootstrap to propose AGENTS.md"})
    save_route(task_dir / "route.json", route)
    write_text(task_dir / f"prompt-{route['current_phase']}.md", prompt_for(task_dir, workspace, route["current_phase"], model))
    return task_dir, workspace, route, model


def cmd_autopilot(args: argparse.Namespace) -> int:
    if (args.native and (args.execute or args.parallel_checks or args.maintainability_review)) or (args.phase and not args.native):
        print("Native routes use recorder commands. --phase requires --native, and native routes do not use adapter execution or parallel lanes.", file=sys.stderr)
        return 2
    if args.phase and args.approval:
        print("Use a full native route to add an approval gate.", file=sys.stderr)
        return 2
    if args.full and not args.execute:
        print("--full requires --execute.", file=sys.stderr)
        return 2
    if args.parallel_checks and not args.full:
        print("--parallel-checks requires --full.", file=sys.stderr)
        return 2
    if args.maintainability_review and not args.full:
        print("--maintainability-review requires --full.", file=sys.stderr)
        return 2
    try:
        task_dir, workspace, route, model = create_task(args)
    except (OSError, ValueError) as exc:
        print(f"Cannot prepare task: {exc}", file=sys.stderr)
        return 2
    model_label = "Model" if args.native else "Model adapter"
    print(f"Task: {task_dir.name}\nWorkspace: {workspace}\nClassification: {route['classification']}\nMode: {route['mode']}\n{model_label}: {model}\nRoute: {' -> '.join(route['phases'])}\nArtifacts: {task_dir}")
    if not args.execute:
        print(f"Prepared prompt: {task_dir / ('prompt-' + route['current_phase'] + '.md')}")
        return 0
    try:
        check_session_writable(task_dir)
        with TaskLock(task_dir):
            if args.full:
                return run_full_cycle(task_dir, workspace, route, model, args.parallel_checks, args.maintainability_review)
            result = run_phase(task_dir, workspace, route, route["current_phase"], model)
            return 0 if result in {0, 4} else result
    except (OSError, ValueError, RuntimeError) as exc:
        print(str(exc), file=sys.stderr)
        return 5


def resolve_task(value: str, override: Path | None = None, workspace: Path | None = None) -> Path:
    candidate = Path(value).expanduser()
    if candidate.is_dir():
        return candidate.resolve()
    roots = session_roots(override, workspace)
    if candidate.name != value:
        raise ValueError(f"task {value!r} not found; use --sessions-root or pass the session directory")
    for root in roots:
        task_dir = root / value
        if (task_dir / "route.json").is_file():
            return task_dir
    searched = ", ".join(str(root) for root in roots)
    raise ValueError(f"task {value!r} not found in {searched}; use --sessions-root or pass the session directory")


def load_runnable_route(task_dir: Path) -> tuple[dict[str, Any], list[str]]:
    raw = read_json(task_dir / "route.json")
    if is_retrospective(raw):
        raise ValueError("retrospective evidence is not a runnable route")
    route, migrations = migrate_route(raw)
    validate_route(route)
    return route, migrations


def is_retrospective(route: dict[str, Any]) -> bool:
    return route.get("provenance") == "retrospective" or route.get("execution") == "retrospective" or route.get("resumable") is False


def cmd_resume(args: argparse.Namespace) -> int:
    try:
        task_dir = resolve_task(args.task, args.sessions_root, args.workspace or Path.cwd())
        check_session_writable(task_dir)
        with TaskLock(task_dir, stale_seconds=args.stale_lock_seconds):
            route, migrations = load_runnable_route(task_dir)
            native = route.get("execution") == "native"
            if native and (args.execute or args.parallel_checks or args.maintainability_review or route["status"] == "running"):
                raise ValueError("use native open, close, or interrupt for native phases")
            recovered = recover_interrupted(route) if not native else False
            telemetry_changed = sync_metrics(task_dir, route, recover=True)
            if migrations or recovered or telemetry_changed:
                save_route(task_dir / "route.json", route)
            if route.get("status") == "needs-review":
                if not args.resolve_review:
                    print("Task is waiting for a human review resolution. Resume with --resolve-review and record the decision.", file=sys.stderr)
                    return 2
                phase = route.get("current_phase")
                if phase not in route.get("phase_states", {}):
                    raise ValueError("needs-review route has no current phase to reopen")
                state = route["phase_states"][phase]
                if state.get("status") in {"succeeded", "needs-review"}:
                    previous_state = state["status"]
                    if previous_state == "succeeded" and "pending" not in ALLOWED_TRANSITIONS.get("succeeded", set()):
                        raise ValueError("phase cannot be reopened under the current transition policy")
                    prior = state.get("last_artifact")
                    if prior and (task_dir / prior).is_file():
                        source = task_dir / prior
                        archive = task_dir / f"{source.stem}-before-human-resolution{source.suffix}"
                        suffix = 2
                        while archive.exists():
                            archive = task_dir / f"{source.stem}-before-human-resolution-{suffix}{source.suffix}"
                            suffix += 1
                        write_text(archive, source.read_text(encoding="utf-8"))
                    if previous_state == "succeeded":
                        state["status"] = "pending"
                        state.pop("finished_at", None)
                        route["completed_phases"] = [done for done in route.get("completed_phases", []) if done != phase]
                        route.setdefault("events", []).append({
                            "event": "phase-reopened", "phase": phase, "from": "succeeded", "to": "pending",
                            "at": utc_now(), "reason": "explicit human review resolution",
                        })
                route["status"] = "prepared"
                route.setdefault("events", []).append({
                    "event": "human-review-resolved", "phase": phase, "at": utc_now(),
                    "reason": args.resolve_review,
                })
                save_route(task_dir / "route.json", route)
            elif args.resolve_review:
                print("--resolve-review applies only to a route waiting for human review.", file=sys.stderr)
                return 2
            workspace = (args.workspace or Path(route.get("workspace") or ".")).expanduser().resolve()
            if not workspace.is_dir():
                raise ValueError(f"workspace is not available: {workspace}")
            model = args.model or route["model"]
            if args.parallel_checks and not route["routing"].get("parallel_checks"):
                route["routing"]["parallel_checks"] = True
                route["events"].append({"event": "parallel-lanes-added", "at": utc_now(), "reason": "human requested parallel checks on resume"})
                save_route(task_dir / "route.json", route)
            if args.maintainability_review and not route.setdefault("routing", {}).get("maintainability_review"):
                route["routing"]["maintainability_review"] = True
                route.setdefault("events", []).append({
                    "event": "review-lane-added", "at": utc_now(),
                    "reason": "human requested maintainability review on resume",
                })
                save_route(task_dir / "route.json", route)
            approval = route["phase_states"].get("approval")
            if approval and approval["status"] == "needs-approval":
                if not args.approve:
                    print("Task is waiting for approval. Use --approve with approved scope and constraints.", file=sys.stderr)
                    return 2
                write_text(task_dir / "approval.md", f"---\nschema_version: \"0.2\"\ntask_id: \"{task_dir.name}\"\nphase: \"approval\"\nstatus: \"ready\"\n---\n\n# Human approval\n\n- Decision: {args.approve}\n- Recorded at: {utc_now()}\n")
                transition(task_dir / "route.json", route, "approval", "succeeded", artifact="approval.md", decision=args.approve)
            if not args.execute:
                print(f"Task is ready to resume: {task_dir}")
                return 0
            if not args.full:
                print("Resume requires --full to preserve route ordering.", file=sys.stderr)
                return 2
            return run_full_cycle(
                task_dir,
                workspace,
                route,
                model,
                bool(route["routing"].get("parallel_checks")),
                bool(route.get("routing", {}).get("maintainability_review")),
            )
    except (OSError, ValueError, RuntimeError, json.JSONDecodeError) as exc:
        print(f"Cannot resume task: {exc}", file=sys.stderr)
        return 2


def cmd_bootstrap(args: argparse.Namespace) -> int:
    if args.adopt:
        if args.write:
            print("Use either --adopt or --write, not both.", file=sys.stderr)
            return 2
        if not args.approve:
            print("--adopt requires --approve with the human review decision.", file=sys.stderr)
            return 2
        try:
            task_dir = resolve_task(args.adopt, args.sessions_root, args.workspace)
            with TaskLock(task_dir):
                route, _ = load_runnable_route(task_dir)
                workspace = Path(route["workspace"]).expanduser().resolve()
                draft = task_dir / "agents-draft.md"
                target = workspace / "AGENTS.md"
                if not draft.is_file():
                    raise ValueError("reviewed agents-draft.md is missing")
                if target.exists():
                    raise ValueError(f"refusing to overwrite existing {target}")
                write_text(target, draft.read_text(encoding="utf-8"))
                for phase in ("approval", "implement", "verify"):
                    route["phase_states"][phase]["status"] = "succeeded"
                route.update({"status": "completed", "current_phase": "verify", "completed_at": utc_now()})
                route["events"].append({"event": "bootstrap-adopted", "at": utc_now(), "reason": args.approve, "artifact": str(target)})
                save_route(task_dir / "route.json", route)
                print(f"Created reviewed project instructions: {target}")
                return 0
        except (OSError, ValueError, RuntimeError, json.JSONDecodeError) as exc:
            print(f"Cannot adopt bootstrap draft: {exc}", file=sys.stderr)
            return 2
    workspace = args.workspace.expanduser().resolve()
    if not workspace.is_dir():
        print(f"Workspace is not a directory: {workspace}", file=sys.stderr)
        return 2
    target = workspace / "AGENTS.md"
    if args.write and not args.approve:
        print("--write requires --approve with the human review decision.", file=sys.stderr)
        return 2
    if args.write and target.exists():
        print(f"Refusing to overwrite existing {target}; prepare a draft for a reviewed manual update.", file=sys.stderr)
        return 2
    task_id = now_id(f"bootstrap-{workspace.name}")
    root = sessions_root(args.sessions_root, workspace)
    try:
        check_session_writable(root)
        task_dir = root / task_id
        task_dir.mkdir()
    except OSError as exc:
        print(f"Cannot prepare bootstrap task: {exc}", file=sys.stderr)
        return 2
    profile = project_profile(workspace)
    draft = agents_draft(profile)
    write_json(task_dir / "project-profile.json", profile)
    write_text(task_dir / "agents-draft.md", draft)
    write_json(task_dir / "route.json", {
        "schema_version": ROUTE_SCHEMA_VERSION, "task_id": task_id, "request": "Bootstrap project AGENTS.md",
        "mode": "change",
        "workspace": str(workspace), "git_branch": current_git_branch(workspace),
        "classification": "standard", "model": "deterministic",
        "status": "needs-approval" if not args.write else "completed", "current_phase": "approval" if not args.write else "verify",
        "phases": ["audit", "approval", "implement", "verify"],
        "phase_states": {
            "audit": {"status": "succeeded", "attempts": 1, "lanes": {"primary": {"status": "succeeded"}}},
            "approval": {"status": "needs-approval" if not args.write else "succeeded", "attempts": 0, "lanes": {"primary": {"status": "pending"}}},
            "implement": {"status": "pending" if not args.write else "succeeded", "attempts": 0, "lanes": {"primary": {"status": "pending"}}},
            "verify": {"status": "pending" if not args.write else "succeeded", "attempts": 0, "lanes": {"primary": {"status": "pending"}}},
        },
        "routing": {"design": False, "approval": True, "maintainability_review": False, "quality_control": False}, "limits": {}, "human_gates": ["approval"],
        "events": [{"event": "bootstrap-draft-created", "at": utc_now(), "reason": "derived from repository evidence"}],
        "telemetry": summarize([]), "created_at": utc_now(),
    })
    if args.write:
        write_text(target, draft)
        print(f"Created reviewed project instructions: {target}")
    else:
        print(f"Draft prepared for human review: {task_dir / 'agents-draft.md'}")
        print(
            "To adopt this exact draft: "
            f'python scripts\\0xSDLC.py bootstrap --adopt "{task_dir}" '
            '--approve "reviewed project instructions"'
        )
    return 0


def cmd_status(args: argparse.Namespace) -> int:
    roots = session_roots(args.sessions_root, Path.cwd())
    found = False
    for tasks in roots:
        if not tasks.exists():
            continue
        found = True
        for route_path in sorted(tasks.glob("*/route.json"), reverse=True):
            try:
                route = read_json(route_path)
                status = "retrospective" if is_retrospective(route) else route.get("status", "invalid")
                print(f"{route.get('task_id', route_path.parent.name)} | {status} | {route.get('classification', '-')} | {route.get('current_phase', '-')} | {route_path.parent}")
            except (OSError, json.JSONDecodeError):
                print(f"{route_path.parent.name} | invalid route.json | {route_path.parent}")
    if not found:
        print("No 0xSDLC tasks yet.")
    return 0


def cmd_native(args: argparse.Namespace) -> int:
    try:
        task_dir = resolve_task(args.task, args.sessions_root, Path.cwd())
        check_session_writable(task_dir)
        with TaskLock(task_dir):
            route, _ = load_runnable_route(task_dir)
            if route.get("execution") != "native":
                raise ValueError("prepare a native route with autopilot --native")
            if args.action == "open":
                attempt, artifact, prompt = open_phase(task_dir, route, args.phase)
                print(json.dumps({"attempt_id": attempt, "artifact": str(task_dir / artifact), "prompt": str(task_dir / prompt)}))
            elif args.action == "close":
                close_phase(task_dir, route, args.attempt, args.outcome)
                print(route["status"])
            else:
                interrupt_phase(task_dir, route, args.attempt)
                print(route["status"])
    except (OSError, ValueError, RuntimeError) as exc:
        print(f"Cannot record native phase: {exc}", file=sys.stderr)
        return 2
    return 0


def cmd_providers(_: argparse.Namespace) -> int:
    errors = validate_profiles()
    if errors:
        print("Provider profile validation failed:\n" + "\n".join(f"- {error}" for error in errors), file=sys.stderr)
        return 1
    print("Provider profiles passed structural conformance: generic, codex, claude, cursor.")
    print("Live CLI authentication, permissions, and interactive discovery still require host-level checks.")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="0xSDLC", description="Lightweight spec-driven agent harness")
    sub = parser.add_subparsers(dest="command", required=True)
    autopilot = sub.add_parser("autopilot", help="prepare or execute a routed SDLC task")
    autopilot.add_argument("request")
    autopilot.add_argument("--workspace", type=Path, default=Path.cwd())
    autopilot.add_argument("--model", default="auto")
    autopilot.add_argument("--kind", choices=sorted(BASE_PHASES))
    design = autopilot.add_mutually_exclusive_group()
    design.add_argument("--with-design", dest="design", action="store_true")
    design.add_argument("--without-design", dest="design", action="store_false")
    autopilot.set_defaults(design=None)
    autopilot.add_argument("--approval", action="store_true")
    autopilot.add_argument("--mode", choices=["auto", "change", "diagnose", "assessment"], default="auto", help="select change, read-only diagnosis, or read-only assessment routing")
    autopilot.add_argument("--execute", action="store_true")
    autopilot.add_argument("--full", action="store_true")
    autopilot.add_argument("--native", action="store_true", help="prepare a route for native-chat phase recording")
    autopilot.add_argument("--phase", choices=sorted(PHASE_ARTIFACTS), help="prepare only the requested native phase")
    autopilot.add_argument("--parallel-checks", action="store_true")
    autopilot.add_argument(
        "--maintainability-review",
        action="store_true",
        help="add one focused review lane plus synthesis; costs two model calls",
    )
    autopilot.add_argument(
        "--quality-control",
        action="store_true",
        help="add the optional evidence-integrity gate after review; costs one model call",
    )
    autopilot.set_defaults(func=cmd_autopilot)

    resume = sub.add_parser("resume", help="recover and continue an existing task")
    resume.add_argument("task")
    resume.add_argument("--workspace", type=Path)
    resume.add_argument("--model")
    resume.add_argument("--approve")
    resume.add_argument("--resolve-review", help="record the human resolution and rerun the stopped phase")
    resume.add_argument("--execute", action="store_true")
    resume.add_argument("--full", action="store_true")
    resume.add_argument("--parallel-checks", action="store_true")
    resume.add_argument("--maintainability-review", action="store_true")
    resume.add_argument("--stale-lock-seconds", type=int, default=1800, help="minimum age to recover a legacy lock whose local owner has exited")
    resume.set_defaults(func=cmd_resume)

    bootstrap = sub.add_parser("bootstrap", help="derive a reviewable AGENTS.md draft from repository evidence")
    bootstrap.add_argument("--workspace", type=Path, default=Path.cwd())
    bootstrap.add_argument("--adopt", metavar="TASK_ID", help="adopt the exact reviewed draft from an existing bootstrap task")
    bootstrap.add_argument("--write", action="store_true", help="create AGENTS.md only when it does not exist")
    bootstrap.add_argument("--approve", help="human review decision required with --write")
    bootstrap.set_defaults(func=cmd_bootstrap)

    status = sub.add_parser("status", help="list generated task routes")
    status.set_defaults(func=cmd_status)
    native = sub.add_parser("native", help="record native-chat phases without a model adapter")
    actions = native.add_subparsers(dest="action", required=True)
    open_native = actions.add_parser("open")
    open_native.add_argument("task")
    open_native.add_argument("phase", choices=sorted(PHASE_ARTIFACTS))
    close_native = actions.add_parser("close")
    close_native.add_argument("task")
    close_native.add_argument("attempt")
    close_native.add_argument("--outcome", choices=["succeeded", "failed", "blocked", "needs-review"], required=True)
    interrupt_native = actions.add_parser("interrupt")
    interrupt_native.add_argument("task")
    interrupt_native.add_argument("attempt")
    for command in (autopilot, resume, bootstrap, status, open_native, close_native, interrupt_native):
        command.add_argument("--sessions-root", type=Path, help="session directory (overrides 0XSDLC_SESSIONS_ROOT)")
    for command in (open_native, close_native, interrupt_native):
        command.set_defaults(func=cmd_native)
    providers = sub.add_parser("providers", help="validate provider capability profiles")
    providers.set_defaults(func=cmd_providers)
    return parser


def main(argv: list[str] | None = None) -> int:
    parsed = build_parser().parse_args(argv)
    return parsed.func(parsed)
