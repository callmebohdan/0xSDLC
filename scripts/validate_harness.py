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
    "docs/operations/autopilot.md",
    "0xSDLC-autopilot/autopilot.md",
    "support/adapters/README.md",
    "support/adapters/cursor.md",
    "support/adapters/generic.md",
    "support/conventions/phase-protocol.md",
    "support/conventions/output-contract.md",
    "support/conventions/evidence-and-status.md",
    "support/conventions/boundaries.md",
    "support/conventions/context-budget.md",
    "support/conventions/version-control.md",
    "support/mcp/README.md",
    "docs/integrations/git.md",
    "support/integrations/README.md",
    "scripts/0xsdlc.py",
    "templates/agent-skill-tests/README.md",
    "templates/design.md",
]

AGENT_PATHS = {
    "autopilot": "0xSDLC-autopilot/autopilot.md",
    "specifier": "support/agents/0xSDLC-spec/specification.md",
    "auditor": "support/agents/0xSDLC-audit/audit.md",
    "architect": "0xSDLC-design/design.md",
    "task-planner": "0xSDLC-plan/planning.md",
    "implementer": "0xSDLC-implement/implementation.md",
    "tester": "support/agents/0xSDLC-test/testing.md",
    "reviewer": "support/agents/0xSDLC-review/review.md",
    "quality-control": "support/agents/0xSDLC-quality/quality-assurance.md",
    "verifier": "0xSDLC-verify/verification.md",
    "fixer": "0xSDLC-fix/fix.md",
}

EXPECTED_LAYOUT = {
    "support/integrations/portable-skills/0xsdlc-agent/SKILL.md",
    "support/integrations/portable-skills/0xsdlc-autopilot/SKILL.md",
    "support/integrations/codex/metadata/0xsdlc-agent/openai.yaml",
    "support/integrations/codex/metadata/0xsdlc-autopilot/openai.yaml",
    "docs/operations/autopilot.md",
    "docs/operations/phase-loading.md",
    "docs/operations/README.md",
}


def main() -> int:
    errors: list[str] = []
    for relative in REQUIRED:
        if not (ROOT / relative).is_file():
            errors.append(f"missing file: {relative}")
    for relative in EXPECTED_LAYOUT:
        if not (ROOT / relative).is_file():
            errors.append(f"missing expected layout file: {relative}")
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
            if manifest.get("schema_version") != "0.2":
                errors.append("manifest must use schema_version 0.2")
        except (OSError, json.JSONDecodeError) as exc:
            errors.append(f"invalid manifest: {exc}")
    for obsolete in (
        "support/0xSDLC-audit",
        "support/0xSDLC-intake",
        "support/0xSDLC-quality",
        "support/0xSDLC-review",
        "support/0xSDLC-spec",
        "support/0xSDLC-test",
        "support/0xSDLC-conventions",
        "support/codex-skills",
        "run-instructions",
    ):
        if (ROOT / obsolete).exists():
            errors.append(f"obsolete path remains: {obsolete}")
    if (ROOT / "templates/tasks.md").exists():
        errors.append("obsolete template remains: templates/tasks.md; use templates/plan.md")
    if errors:
        print("Harness validation failed:")
        print("\n".join(f"- {error}" for error in errors))
        return 1
    print("Harness validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
