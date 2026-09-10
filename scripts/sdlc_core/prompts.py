"""Minimal phase packet assembly."""

from __future__ import annotations

import json
import os
from pathlib import Path

from .config import PHASE_AGENTS, PHASE_ARTIFACTS, PHASE_CONTRACTS, library_path


def sibling_artifact(artifact: str, label: str) -> str:
    path = Path(artifact)
    return f"{path.stem}-{label}{path.suffix}"


def prompt_for(task_dir: Path, workspace: Path, phase: str, model: str, lane: str = "primary", output_artifact: str | None = None) -> str:
    contract = library_path(PHASE_CONTRACTS.get(phase, "support/adapters/generic.md"))
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
    if phase == "synthesis" and output_artifact:
        primary_path = Path(output_artifact)
        primary = primary_path.with_name(primary_path.stem.removesuffix("-synthesis") + primary_path.suffix).name
        synthesis_inputs = f"\nReconcile only `{primary}` and `{sibling_artifact(primary, 'secondary')}` for source phase `{lane}`. Do not change source.\n"
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
## Global boundaries

{library_path('support/0xSDLC-conventions/boundaries.md').read_text(encoding='utf-8')}
"""
