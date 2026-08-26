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
    "scripts/0xsdlc.py",
    "templates/agent-skill-tests/README.md",
    "templates/design.md",
]

AGENT_PATHS = {
    "autopilot": "0xSDLC-autopilot/autopilot.md",
    "intake": "support/0xSDLC-intake/intake.md",
    "specifier": "support/0xSDLC-spec/specification.md",
    "auditor": "support/0xSDLC-audit/audit.md",
    "architect": "0xSDLC-design/design.md",
    "task-planner": "0xSDLC-plan/planning.md",
    "implementer": "0xSDLC-implement/implementation.md",
    "tester": "support/0xSDLC-test/testing.md",
    "reviewer": "support/0xSDLC-review/review.md",
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
    if errors:
        print("Harness validation failed:")
        print("\n".join(f"- {error}" for error in errors))
        return 1
    print("Harness validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
