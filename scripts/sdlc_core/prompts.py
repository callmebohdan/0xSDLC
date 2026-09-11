"""Minimal phase packet assembly."""

from __future__ import annotations

import json
import os
from pathlib import Path

from .config import PHASE_AGENTS, PHASE_ARTIFACTS, PHASE_CONTRACTS, library_path
from .storage import read_json


def sibling_artifact(artifact: str, label: str) -> str:
    path = Path(artifact)
    return f"{path.stem}-{label}{path.suffix}"


PRACTICE_PHASES = {
    "design": ("support/engineering-practices/architecture.md", "support/engineering-practices/design-patterns.md"),
    "implement": ("support/engineering-practices/maintainability.md",),
    "fix": ("support/engineering-practices/maintainability.md",),
}
LANGUAGE_PROFILES = {"C++": "support/engineering-practices/languages/cpp.md"}


def selected_practice_paths(task_dir: Path, phase: str, lane: str) -> list[str]:
    """Select only phase- and language-relevant supplements to cap prompt cost."""
    selected = list(PRACTICE_PHASES.get(phase, ()))
    if lane == "maintainability":
        selected = [
            "support/engineering-practices/maintainability.md",
            "support/engineering-practices/architecture.md",
            "support/engineering-practices/design-patterns.md",
        ]
    profile_path = task_dir / "project-profile.json"
    if profile_path.is_file() and (phase in {"design", "implement", "fix", "test", "review"} or lane == "maintainability"):
        languages = read_json(profile_path).get("languages", {})
        route = read_json(task_dir / "route.json") if (task_dir / "route.json").is_file() else {}
        dedicated_review = phase == "review" and route.get("routing", {}).get("maintainability_review")
        if not dedicated_review or lane == "maintainability":
            selected.extend(path for language, path in LANGUAGE_PROFILES.items() if language in languages)
    return list(dict.fromkeys(selected))


def practice_context(task_dir: Path, phase: str, lane: str) -> str:
    paths = selected_practice_paths(task_dir, phase, lane)
    if not paths:
        return ""
    sections = []
    for relative in paths:
        path = library_path(relative)
        if path.is_file():
            sections.append(f"### {relative}\n\n{path.read_text(encoding='utf-8')}")
    if not sections:
        return ""
    return "\n## Applicable engineering practices\n\nProject instructions and checked-in tool configuration override these generic supplements.\n\n" + "\n\n".join(sections) + "\n"


def prompt_for(
    task_dir: Path,
    workspace: Path,
    phase: str,
    model: str,
    lane: str = "primary",
    output_artifact: str | None = None,
    evidence_inputs: list[str] | None = None,
) -> str:
    contract_relative = "support/engineering-practices/maintainability-review.md" if lane == "maintainability" else PHASE_CONTRACTS.get(phase, "support/adapters/generic.md")
    contract = library_path(contract_relative)
    if not contract.is_file():
        contract = library_path("support/adapters/generic.md")
    route = json.loads((task_dir / "route.json").read_text(encoding="utf-8"))
    names = sorted(path.name for path in task_dir.iterdir() if path.is_file() and not path.name.startswith("adapter-"))
    project_instructions = workspace / "AGENTS.md"
    project_context = ""
    if project_instructions.is_file():
        project_context = f"\n## Project instructions\n\n{project_instructions.read_text(encoding='utf-8', errors='replace')}\n"
    else:
        project_context = "\n## Project instructions\n\nNo root `AGENTS.md` exists. Use `project-context.md` if supplied; do not invent repository commands or conventions.\n"
    synthesis_inputs = ""
    if phase == "synthesis" and evidence_inputs:
        listed = ", ".join(f"`{name}`" for name in evidence_inputs)
        synthesis_inputs = f"\nReconcile only {listed} for source phase `{lane}`. Do not change source.\n"
    return f"""# 0xSDLC phase packet

Task ID: `{task_dir.name}`
Model adapter: `{model}`
Phase: `{phase}`
Agent: `{PHASE_AGENTS.get(phase, 'orchestrator')}`
Lane: `{lane}`
Workspace: `{workspace}`

## Outcome and evidence rule

Perform only this phase. Write `{output_artifact or PHASE_ARTIFACTS.get(phase, f'{phase}.md')}` in `{task_dir}` with valid front matter. Report only evidence obtained. Stop for missing proof or approval. Do not fill gaps with plausible reasoning.

## Route

```json
{json.dumps(route, indent=2)}
```

## Available task artifacts

{os.linesep.join(f'- `{name}`' for name in names)}
{synthesis_inputs}

## Phase contract

{contract.read_text(encoding='utf-8')}
{project_context}
{practice_context(task_dir, phase, lane)}
## Global boundaries

{library_path('support/conventions/boundaries.md').read_text(encoding='utf-8')}
"""
