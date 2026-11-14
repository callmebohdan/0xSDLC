"""Stable constants and path resolution for 0xSDLC."""

from __future__ import annotations

import os
from pathlib import Path


HARNESS_ROOT = Path(__file__).resolve().parents[2]
ROUTE_SCHEMA_VERSION = "0.5"
ARTIFACT_SCHEMA_VERSION = "0.2"
MAX_FIX_ATTEMPTS_PER_FINDING = 2
MAX_TOTAL_FIX_ATTEMPTS = 4
VALID_ARTIFACT_STATUS = {"ready", "needs-review", "blocked", "verified"}

PHASE_CONTRACTS = {
    "specify": "support/agents/0xSDLC-spec/specification.md",
    "audit": "support/agents/0xSDLC-audit/audit.md",
    "design": "0xSDLC-design/design.md",
    "plan": "0xSDLC-plan/planning.md",
    "implement": "0xSDLC-implement/implementation.md",
    "test": "support/agents/0xSDLC-test/testing.md",
    "review": "support/agents/0xSDLC-review/review.md",
    "quality-control": "support/agents/0xSDLC-quality/quality-assurance.md",
    "verify": "0xSDLC-verify/verification.md",
    "fix": "0xSDLC-fix/fix.md",
    "synthesis": "support/conventions/parallel-synthesis.md",
}
PHASE_ARTIFACTS = {
    "specify": "spec.md", "audit": "audit.md", "design": "design.md",
    "plan": "plan.md", "implement": "implementation.md", "test": "test-report.md",
    "review": "review.md", "verify": "verification.md", "fix": "fix-report.md",
    "quality-control": "quality-report.md",
    "synthesis": "synthesis.md",
}
PHASE_AGENTS = {
    "specify": "specifier", "audit": "auditor", "design": "architect",
    "plan": "task-planner", "implement": "implementer", "test": "tester",
    "review": "reviewer", "verify": "verifier", "fix": "fixer",
    "quality-control": "quality-control",
    "synthesis": "evidence-synthesizer",
}
BASE_PHASES = {
    "small": ["audit", "plan", "implement", "test", "review", "verify"],
    "standard": ["specify", "audit", "plan", "implement", "test", "review", "verify"],
    "high-risk": ["specify", "audit", "design", "plan", "approval", "implement", "test", "review", "verify"],
}
ALLOWED_TRANSITIONS = {
    "pending": {"running", "needs-approval", "skipped"},
    "running": {"succeeded", "failed", "blocked", "needs-approval", "needs-review"},
    "succeeded": {"running", "pending"},
    "failed": {"running", "blocked"},
    "blocked": {"running"},
    "needs-approval": {"running", "succeeded"},
    "needs-review": {"running"},
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


def project_root(workspace: Path | None = None) -> Path:
    """Find the Git repository root, or use the supplied workspace as the project root."""
    location = (workspace or Path.cwd()).expanduser().resolve()
    if not location.is_dir():
        location = location.parent
    for candidate in (location, *location.parents):
        if (candidate / ".git").exists():
            return candidate
    return location


def legacy_sessions_root() -> Path:
    """Return the user-level session directory used before project-local storage."""
    return system_library() / "sessions"


def sessions_root(override: Path | None = None, workspace: Path | None = None) -> Path:
    configured = os.environ.get("0XSDLC_SESSIONS_ROOT")
    if override is not None or configured:
        return Path(override if override is not None else configured).expanduser().resolve()
    return project_root(workspace) / ".agents" / "0xSDLC" / "sessions"


def session_roots(override: Path | None = None, workspace: Path | None = None) -> list[Path]:
    """Return the selected root and legacy roots for default lookup."""
    selected = sessions_root(override, workspace)
    if override is not None or os.environ.get("0XSDLC_SESSIONS_ROOT"):
        return [selected]
    project = project_root(workspace)
    legacy_roots = [(project / ".agents" / "0xsdlc" / "sessions").resolve()]
    logs = project / "logs"
    if logs.is_dir():
        legacy_roots.extend(path.resolve() for path in logs.iterdir() if path.is_dir())
    legacy_roots.append(legacy_sessions_root().resolve())
    return list(dict.fromkeys([selected, *legacy_roots]))
