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
    "support/conventions/parallel-synthesis.md",
    "support/conventions/context-budget.md",
    "support/conventions/version-control.md",
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
    "support/agents/0xSDLC-bootstrap/bootstrap.md",
    "support/integrations/README.md",
    "support/integrations/portable-skills/0xsdlc-autopilot/SKILL.md",
    "support/integrations/portable-skills/0xsdlc-agent/SKILL.md",
    "support/integrations/portable-skills/0xsdlc-bootstrap/SKILL.md",
    "support/integrations/codex/metadata/0xsdlc-autopilot/openai.yaml",
    "support/integrations/codex/metadata/0xsdlc-agent/openai.yaml",
    "support/integrations/codex/metadata/0xsdlc-bootstrap/openai.yaml",
    "support/mcp/README.md",
    "docs/integrations/git.md",
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
    "project-bootstrap": "support/agents/0xSDLC-bootstrap/bootstrap.md",
    "specifier": "support/agents/0xSDLC-spec/specification.md",
    "auditor": "support/agents/0xSDLC-audit/audit.md",
    "architect": "0xSDLC-design/design.md",
    "task-planner": "0xSDLC-plan/planning.md",
    "implementer": "0xSDLC-implement/implementation.md",
    "tester": "support/agents/0xSDLC-test/testing.md",
    "reviewer": "support/agents/0xSDLC-review/review.md",
    "maintainability-reviewer": "support/engineering-practices/maintainability-review.md",
    "quality-control": "support/agents/0xSDLC-quality/quality-assurance.md",
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
            if manifest.get("schema_version") != "0.4":
                errors.append("manifest must use schema_version 0.4")
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
    for obsolete in (
        "support/0xSDLC-audit",
        "support/0xSDLC-bootstrap",
        "support/0xSDLC-conventions",
        "support/0xSDLC-intake",
        "support/0xSDLC-quality",
        "support/0xSDLC-review",
        "support/0xSDLC-spec",
        "support/0xSDLC-test",
        "support/codex-skills",
        "support/skills",
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
