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

from .config import BASE_PHASES, library_path, sessions_root
from .project import agents_draft, project_profile
from .prompts import prompt_for
from .providers import select_model, validate_profiles
from .routing import classify, migrate_route, needs_design, route_payload
from .runner import run_full_cycle, run_phase, save_route, transition
from .schemas import validate_route
from .storage import TaskLock, read_json, recover_interrupted, utc_now, write_json, write_text


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
    tasks = sessions_root()
    tasks.mkdir(parents=True, exist_ok=True)
    task_id = now_id(args.request)
    task_dir = tasks / task_id
    task_dir.mkdir()
    model, kind = select_model(args.model), args.kind or classify(args.request)
    include_design = True if kind == "high-risk" else (args.design if args.design is not None else needs_design(args.request, kind))
    route = route_payload(task_id, args.request, kind, model, include_design, args.approval or kind == "high-risk", str(workspace))
    write_text(task_dir / "brief.md", render_template(library_path("templates/brief.md"), {"task_id": task_id, "request": args.request}))
    if not (workspace / "AGENTS.md").is_file():
        profile = project_profile(workspace)
        write_json(task_dir / "project-profile.json", profile)
        write_text(task_dir / "project-context.md", agents_draft(profile))
        route["events"].append({"event": "project-instructions-missing", "at": utc_now(), "reason": "using task-local project context; run bootstrap to propose AGENTS.md"})
    save_route(task_dir / "route.json", route)
    write_text(task_dir / f"prompt-{route['current_phase']}.md", prompt_for(task_dir, workspace, route["current_phase"], model))
    return task_dir, workspace, route, model


def cmd_autopilot(args: argparse.Namespace) -> int:
    if args.full and not args.execute:
        print("--full requires --execute.", file=sys.stderr)
        return 2
    if args.parallel_checks and not args.full:
        print("--parallel-checks requires --full.", file=sys.stderr)
        return 2
    try:
        task_dir, workspace, route, model = create_task(args)
    except (OSError, ValueError) as exc:
        print(f"Cannot prepare task: {exc}", file=sys.stderr)
        return 2
    print(f"Task: {task_dir.name}\nWorkspace: {workspace}\nClassification: {route['classification']}\nModel adapter: {model}\nRoute: {' -> '.join(route['phases'])}\nArtifacts: {task_dir}")
    if not args.execute:
        print(f"Prepared prompt: {task_dir / ('prompt-' + route['current_phase'] + '.md')}")
        return 0
    try:
        with TaskLock(task_dir):
            if args.full:
                return run_full_cycle(task_dir, workspace, route, model, args.parallel_checks)
            result = run_phase(task_dir, workspace, route, route["current_phase"], model)
            return 0 if result in {0, 4} else result
    except RuntimeError as exc:
        print(str(exc), file=sys.stderr)
        return 5


def resolve_task(value: str) -> Path:
    candidate = Path(value).expanduser()
    if candidate.is_dir():
        return candidate.resolve()
    matches = list(sessions_root().glob(f"{value}/route.json"))
    if len(matches) != 1:
        raise ValueError(f"task not found or ambiguous: {value}")
    return matches[0].parent


def cmd_resume(args: argparse.Namespace) -> int:
    try:
        task_dir = resolve_task(args.task)
        with TaskLock(task_dir, stale_seconds=args.stale_lock_seconds):
            route, migrations = migrate_route(read_json(task_dir / "route.json"))
            recovered = recover_interrupted(route)
            if migrations or recovered:
                save_route(task_dir / "route.json", route)
            validate_route(route)
            workspace = (args.workspace or Path(route.get("workspace") or ".")).expanduser().resolve()
            if not workspace.is_dir():
                raise ValueError(f"workspace is not available: {workspace}")
            model = args.model or route["model"]
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
            return run_full_cycle(task_dir, workspace, route, model, args.parallel_checks)
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
            task_dir = resolve_task(args.adopt)
            with TaskLock(task_dir):
                route, _ = migrate_route(read_json(task_dir / "route.json"))
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
    task_dir = sessions_root() / task_id
    task_dir.mkdir(parents=True)
    profile = project_profile(workspace)
    draft = agents_draft(profile)
    write_json(task_dir / "project-profile.json", profile)
    write_text(task_dir / "agents-draft.md", draft)
    write_json(task_dir / "route.json", {
        "schema_version": "0.4", "task_id": task_id, "request": "Bootstrap project AGENTS.md",
        "workspace": str(workspace), "classification": "standard", "model": "deterministic",
        "status": "needs-approval" if not args.write else "completed", "current_phase": "approval" if not args.write else "verify",
        "phases": ["audit", "approval", "implement", "verify"],
        "phase_states": {
            "audit": {"status": "succeeded", "attempts": 1, "lanes": {"primary": {"status": "succeeded"}}},
            "approval": {"status": "needs-approval" if not args.write else "succeeded", "attempts": 0, "lanes": {"primary": {"status": "pending"}}},
            "implement": {"status": "pending" if not args.write else "succeeded", "attempts": 0, "lanes": {"primary": {"status": "pending"}}},
            "verify": {"status": "pending" if not args.write else "succeeded", "attempts": 0, "lanes": {"primary": {"status": "pending"}}},
        },
        "routing": {"design": False, "approval": True}, "limits": {}, "human_gates": ["approval"],
        "events": [{"event": "bootstrap-draft-created", "at": utc_now(), "reason": "derived from repository evidence"}],
        "telemetry": {"calls": 0, "duration_ms": 0, "input_tokens": 0, "output_tokens": 0, "cost_usd": 0.0}, "created_at": utc_now(),
    })
    if args.write:
        write_text(target, draft)
        print(f"Created reviewed project instructions: {target}")
    else:
        print(f"Draft prepared for human review: {task_dir / 'agents-draft.md'}")
        print(
            "To adopt this exact draft: "
            f"python scripts\\0xSDLC.py bootstrap --adopt {task_id} "
            '--approve "reviewed project instructions"'
        )
    return 0


def cmd_status(_: argparse.Namespace) -> int:
    tasks = sessions_root()
    if not tasks.exists():
        print("No 0xSDLC tasks yet.")
        return 0
    for route_path in sorted(tasks.glob("*/route.json"), reverse=True):
        try:
            route = read_json(route_path)
            print(f"{route.get('task_id', route_path.parent.name)} | {route.get('status', 'invalid')} | {route.get('classification', '-')} | {route.get('current_phase', '-')}")
        except (OSError, json.JSONDecodeError):
            print(f"{route_path.parent.name} | invalid route.json")
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
    autopilot.add_argument("--execute", action="store_true")
    autopilot.add_argument("--full", action="store_true")
    autopilot.add_argument("--parallel-checks", action="store_true")
    autopilot.set_defaults(func=cmd_autopilot)

    resume = sub.add_parser("resume", help="recover and continue an existing task")
    resume.add_argument("task")
    resume.add_argument("--workspace", type=Path)
    resume.add_argument("--model")
    resume.add_argument("--approve")
    resume.add_argument("--execute", action="store_true")
    resume.add_argument("--full", action="store_true")
    resume.add_argument("--parallel-checks", action="store_true")
    resume.add_argument("--stale-lock-seconds", type=int, default=1800)
    resume.set_defaults(func=cmd_resume)

    bootstrap = sub.add_parser("bootstrap", help="derive a reviewable AGENTS.md draft from repository evidence")
    bootstrap.add_argument("--workspace", type=Path, default=Path.cwd())
    bootstrap.add_argument("--adopt", metavar="TASK_ID", help="adopt the exact reviewed draft from an existing bootstrap task")
    bootstrap.add_argument("--write", action="store_true", help="create AGENTS.md only when it does not exist")
    bootstrap.add_argument("--approve", help="human review decision required with --write")
    bootstrap.set_defaults(func=cmd_bootstrap)

    status = sub.add_parser("status", help="list generated task routes")
    status.set_defaults(func=cmd_status)
    providers = sub.add_parser("providers", help="validate provider capability profiles")
    providers.set_defaults(func=cmd_providers)
    return parser


def main(argv: list[str] | None = None) -> int:
    parsed = build_parser().parse_args(argv)
    return parsed.func(parsed)
