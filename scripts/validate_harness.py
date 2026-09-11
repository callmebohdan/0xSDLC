"""Dependency-free structural checks for the 0xSDLC harness."""

from __future__ import annotations

import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REQUIRED = [
    "README.md",
    "AGENTS.md",
    "docs/agent-library.md",
    "orchestrator/manifest.json",
    "run-instructions/autopilot.md",
    "0xSDLC-autopilot/autopilot.md",
    "support/adapters/README.md",
    "support/adapters/cursor.md",
    "support/adapters/generic.md",
    "support/0xSDLC-conventions/phase-protocol.md",
    "support/0xSDLC-conventions/output-contract.md",
    "support/0xSDLC-conventions/evidence-and-status.md",
    "support/0xSDLC-conventions/boundaries.md",
    "support/0xSDLC-conventions/parallel-synthesis.md",
    "support/engineering-practices/README.md",
    "support/engineering-practices/maintainability.md",
    "support/engineering-practices/architecture.md",
    "support/engineering-practices/design-patterns.md",
    "support/engineering-practices/maintainability-review.md",
    "support/engineering-practices/languages/cpp.md",
    "docs/evaluation.md",
    "docs/engineering-quality.md",
    "docs/naming.md",
    "docs/references.md",
    "scripts/0xSDLC.py",
    "scripts/sdlc_core/cli.py",
    "scripts/sdlc_core/runner.py",
    "scripts/sdlc_core/routing.py",
    "scripts/sdlc_core/artifacts.py",
    "scripts/sdlc_core/storage.py",
    "scripts/sdlc_core/providers.py",
    "scripts/sdlc_core/telemetry.py",
    "scripts/sdlc_core/project.py",
    "support/0xSDLC-bootstrap/bootstrap.md",
    "support/skills/0xsdlc-autopilot/SKILL.md",
    "support/skills/0xsdlc-agent/SKILL.md",
    "support/skills/0xsdlc-bootstrap/SKILL.md",
    "schemas/route.schema.json",
    "schemas/artifact.schema.json",
    "support/adapters/profiles/generic.json",
    "support/adapters/profiles/codex.json",
    "support/adapters/profiles/claude.json",
    "support/adapters/profiles/cursor.json",
    "templates/agent-skill-tests/README.md",
    "templates/design.md",
    "templates/maintainability-review.md",
]

AGENT_PATHS = {
    "autopilot": "0xSDLC-autopilot/autopilot.md",
    "project-bootstrap": "support/0xSDLC-bootstrap/bootstrap.md",
    "specifier": "support/0xSDLC-spec/specification.md",
    "auditor": "support/0xSDLC-audit/audit.md",
    "architect": "0xSDLC-design/design.md",
    "task-planner": "0xSDLC-plan/planning.md",
    "implementer": "0xSDLC-implement/implementation.md",
    "tester": "support/0xSDLC-test/testing.md",
    "reviewer": "support/0xSDLC-review/review.md",
    "maintainability-reviewer": "support/engineering-practices/maintainability-review.md",
    "quality-control": "support/0xSDLC-quality/quality-assurance.md",
    "verifier": "0xSDLC-verify/verification.md",
    "fixer": "0xSDLC-fix/fix.md",
}


def main() -> int:
    errors: list[str] = []
    for relative in REQUIRED:
        if not (ROOT / relative).is_file():
            errors.append(f"missing file: {relative}")
    manifest_path = ROOT / "orchestrator/manifest.json"
    if manifest_path.exists():
        try:
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            for agent in manifest.get("agents", []):
                relative = AGENT_PATHS.get(agent)
                if relative is None:
                    errors.append(f"unknown agent in manifest: {agent}")
                    continue
                path = ROOT / relative
                if not path.is_file():
                    errors.append(f"missing agent contract: {path.relative_to(ROOT)}")
            for artifact in manifest.get("artifacts", []):
                path = ROOT / "templates" / artifact
                if not path.is_file():
                    errors.append(f"missing template: {path.relative_to(ROOT)}")
        except (OSError, json.JSONDecodeError) as exc:
            errors.append(f"invalid manifest: {exc}")
    for relative in (
        "schemas/route.schema.json",
        "schemas/artifact.schema.json",
        "support/adapters/profiles/generic.json",
        "support/adapters/profiles/codex.json",
        "support/adapters/profiles/claude.json",
        "support/adapters/profiles/cursor.json",
    ):
        path = ROOT / relative
        if path.exists():
            try:
                json.loads(path.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError) as exc:
                errors.append(f"invalid JSON: {relative}: {exc}")
    if errors:
        print("Harness validation failed:")
        print("\n".join(f"- {error}" for error in errors))
        return 1
    print("Harness validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
