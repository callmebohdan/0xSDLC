"""Stable constants and path resolution for 0xSDLC."""

from __future__ import annotations

import os
from pathlib import Path


HARNESS_ROOT = Path(__file__).resolve().parents[2]
ROUTE_SCHEMA_VERSION = "0.4"
ARTIFACT_SCHEMA_VERSION = "0.2"
MAX_FIX_ATTEMPTS_PER_FINDING = 2
MAX_TOTAL_FIX_ATTEMPTS = 4
VALID_ARTIFACT_STATUS = {"ready", "needs-review", "blocked", "verified"}

PHASE_CONTRACTS = {
    "specify": "support/0xSDLC-spec/specification.md",
    "audit": "support/0xSDLC-audit/audit.md",
    "design": "0xSDLC-design/design.md",
    "plan": "0xSDLC-plan/planning.md",
    "implement": "0xSDLC-implement/implementation.md",
    "test": "support/0xSDLC-test/testing.md",
    "review": "support/0xSDLC-review/review.md",
    "verify": "0xSDLC-verify/verification.md",
    "fix": "0xSDLC-fix/fix.md",
    "synthesis": "support/0xSDLC-conventions/parallel-synthesis.md",
}
PHASE_ARTIFACTS = {
    "specify": "spec.md", "audit": "audit.md", "design": "design.md",
    "plan": "plan.md", "implement": "implementation.md", "test": "test-report.md",
    "review": "review.md", "verify": "verification.md", "fix": "fix-report.md",
    "synthesis": "synthesis.md",
}
PHASE_AGENTS = {
    "specify": "specifier", "audit": "auditor", "design": "architect",
    "plan": "task-planner", "implement": "implementer", "test": "tester",
    "review": "reviewer", "verify": "verifier", "fix": "fixer",
    "synthesis": "evidence-synthesizer",
}
BASE_PHASES = {
    "small": ["audit", "plan", "implement", "test", "review", "verify"],
    "standard": ["specify", "audit", "plan", "implement", "test", "review", "verify"],
    "high-risk": ["specify", "audit", "design", "plan", "approval", "implement", "test", "review", "verify"],
}
ALLOWED_TRANSITIONS = {
    "pending": {"running", "needs-approval", "skipped"},
    "running": {"succeeded", "failed", "blocked", "needs-approval"},
    "succeeded": {"running"},
    "failed": {"running", "blocked"},
    "blocked": {"running"},
    "needs-approval": {"running", "succeeded"},
    "skipped": set(),
}


def system_library() -> Path:
    override = os.environ.get("0XSDLC_AGENTS_HOME")
    if override:
        return Path(override).expanduser().resolve()
    return (Path.home() / ".agents" / "0xsdlc").resolve()


def library_path(relative: str) -> Path:
    installed = system_library() / relative
    return installed if installed.exists() else HARNESS_ROOT / relative


def sessions_root() -> Path:
    return system_library() / "sessions"
