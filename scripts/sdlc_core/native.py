"""Native-chat phase boundaries without launching a model adapter."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from .artifacts import validate_artifact
from .config import PHASE_ARTIFACTS
from .prompts import prompt_for
from .routing import apply_route_directives
from .runner import finish_attempt, reserve_artifact, save_route, start_attempt, transition
from .storage import recover_interrupted, utc_now, write_text


def open_phase(task_dir: Path, route: dict[str, Any], phase: str) -> tuple[str, str, str]:
    if route["status"] in {"running", "needs-review", "needs-approval", "completed"}:
        raise ValueError(f"native route cannot open a phase while {route['status']}")
    states = route["phase_states"]
    expected = next((name for name in route["phases"] if states[name]["status"] not in {"succeeded", "skipped"}), None)
    if phase != expected or phase == "approval":
        raise ValueError(f"cannot open {phase}; next routed phase is {expected}")
    workspace = Path(route["workspace"])
    attempt = start_attempt(task_dir, workspace, route, phase)
    state = states[phase]
    artifact = reserve_artifact(task_dir, state, PHASE_ARTIFACTS[phase])
    prompt = f"attempts/{attempt['attempt_id']}/prompt-{phase}.md"
    attempt["prompt"] = prompt
    state["lanes"]["primary"] = {"status": "running", "artifact": artifact}
    save_route(task_dir / "route.json", route)
    write_text(task_dir / prompt, prompt_for(task_dir, workspace, phase, route["model"], output_artifact=artifact))
    return attempt["attempt_id"], artifact, prompt


def close_phase(task_dir: Path, route: dict[str, Any], attempt_id: str, outcome: str) -> None:
    phase = route["current_phase"]
    state = route["phase_states"][phase]
    if state["status"] != "running" or state.get("attempt_id") != attempt_id:
        raise ValueError(f"no open native phase for attempt {attempt_id}")
    artifact = state["attempt_history"][-1]["artifacts"][0]
    metadata = validate_artifact(task_dir / artifact, task_dir.name, phase)
    if metadata["status"] in {"blocked", "needs-review"}:
        outcome = metadata["status"]
    if outcome == "succeeded" and (
        (phase == "test" and metadata.get("test_outcome") != "pass")
        or (phase == "review" and metadata.get("decision") != "approve")
    ):
        outcome = "needs-review"
    state["lanes"]["primary"]["status"] = outcome
    state["last_artifact"] = artifact
    if outcome == "succeeded":
        if not route.get("standalone_phase"):
            apply_route_directives(route, metadata, phase)
        route.setdefault("completed_phases", []).append(phase)
    route_path = task_dir / "route.json"
    finish_attempt(task_dir, Path(route["workspace"]), route, phase, outcome, persist=False, artifacts=[artifact])
    if outcome == "succeeded":
        index = route["phases"].index(phase) + 1
        if index == len(route["phases"]):
            route.update(status="completed", completed_at=utc_now())
        elif route["phases"][index] == "approval":
            transition(route_path, route, "approval", "needs-approval", persist=False)
    save_route(route_path, route)


def interrupt_phase(task_dir: Path, route: dict[str, Any], attempt_id: str) -> None:
    state = route["phase_states"][route["current_phase"]]
    if state["status"] != "running" or state.get("attempt_id") != attempt_id:
        raise ValueError(f"no open native phase for attempt {attempt_id}")
    recover_interrupted(route)
    save_route(task_dir / "route.json", route)
