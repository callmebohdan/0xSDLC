"""Initial and evidence-driven route decisions."""

from __future__ import annotations

import re
from typing import Any

from .artifacts import list_value
from .config import BASE_PHASES, MAX_FIX_ATTEMPTS_PER_FINDING, MAX_TOTAL_FIX_ATTEMPTS, ROUTE_SCHEMA_VERSION
from .storage import utc_now


def classify(request: str) -> str:
    high_risk = re.compile(r"\b(auth|authentication|authorization|security|secret|credential|password|migration|database|deploy|deployment|production|billing|payment|public api|delete)\b", re.I)
    if high_risk.search(request):
        return "high-risk"
    if len(request.split()) <= 14 and re.search(r"\b(fix|rename|typo|format|small|add test|update readme)\b", request, re.I):
        return "small"
    return "standard"


def needs_design(request: str, kind: str) -> bool:
    if kind == "high-risk":
        return True
    return bool(re.search(r"\b(architecture|integrat(?:e|ion)|cross[- ](?:module|service)|new (?:service|storage|workflow)|data model|protocol|concurren|performance)\b", request, re.I))


def infer_mode(request: str, requested: str = "auto") -> str:
    if requested != "auto":
        return requested
    if re.search(r"\b(diagnos(?:e|is)|investigate|why\s+(?:is|does|did)|root cause)\b", request, re.I):
        return "diagnose"
    change_intent = re.search(r"\b(implement|build|add|create|change|update|refactor|fix|remove|rename|migrate)\b", request, re.I)
    if not change_intent and re.search(r"\b(assess|assessment|analy[sz]e|research|review|audit|find\s+(?:gaps|issues))\b", request, re.I):
        return "assessment"
    return "change"


def route_for(
    kind: str,
    include_design: bool,
    require_approval: bool,
    mode: str = "change",
    quality_control: bool = False,
) -> list[str]:
    if mode == "diagnose":
        phases = ["audit", "test", "review", "verify"]
    elif mode == "assessment":
        phases = ["specify", "audit", "plan", "review", "verify"]
    else:
        phases = list(BASE_PHASES[kind])
    if not include_design and "design" in phases:
        phases.remove("design")
    if include_design and mode != "diagnose" and "design" not in phases:
        phases.insert(phases.index("plan"), "design")
    if require_approval and "implement" in phases and "approval" not in phases:
        phases.insert(phases.index("implement"), "approval")
    if quality_control and "review" in phases and "quality-control" not in phases:
        phases.insert(phases.index("review") + 1, "quality-control")
    return phases


def route_payload(
    task_id: str,
    request: str,
    kind: str,
    model: str,
    include_design: bool,
    require_approval: bool,
    workspace: str,
    maintainability_review: bool = False,
    mode: str = "change",
    quality_control: bool = False,
) -> dict[str, Any]:
    phases = route_for(kind, include_design, require_approval, mode, quality_control)
    include_design = "design" in phases
    require_approval = "approval" in phases
    return {
        "schema_version": ROUTE_SCHEMA_VERSION,
        "task_id": task_id,
        "request": request,
        "workspace": workspace,
        "classification": kind,
        "mode": mode,
        "model": model,
        "status": "prepared",
        "current_phase": phases[0],
        "phases": phases,
        "routing": {"design": include_design, "approval": require_approval, "maintainability_review": maintainability_review, "quality_control": quality_control},
        "limits": {"per_finding_fix_attempts": MAX_FIX_ATTEMPTS_PER_FINDING, "total_fix_attempts": MAX_TOTAL_FIX_ATTEMPTS},
        "human_gates": ["approval"] if "approval" in phases else [],
        "phase_states": {phase: {"status": "pending", "attempts": 0, "lanes": {"primary": {"status": "pending"}}} for phase in phases},
        "events": [{"event": "route-prepared", "at": utc_now(), "reason": f"classified as {kind} risk in {mode} mode"}],
        "telemetry": {"calls": 0, "duration_ms": 0, "input_tokens": 0, "output_tokens": 0, "cost_usd": 0.0},
        "created_at": utc_now(),
    }


def migrate_route(route: dict[str, Any]) -> tuple[dict[str, Any], list[str]]:
    """Upgrade older route schemas in memory while retaining an explicit migration trail."""
    source = str(route.get("schema_version", "0.2"))
    if source not in {"0.2", "0.3", "0.4", ROUTE_SCHEMA_VERSION}:
        raise ValueError(f"unsupported route schema {source!r}")
    changes: list[str] = []
    if source in {"0.2", "0.3", "0.4"}:
        route.setdefault("workspace", str(route.get("workspace") or ""))
        route.setdefault("routing", {"design": "design" in route.get("phases", []), "approval": "approval" in route.get("phases", [])})
        route.setdefault("limits", {"per_finding_fix_attempts": MAX_FIX_ATTEMPTS_PER_FINDING, "total_fix_attempts": MAX_TOTAL_FIX_ATTEMPTS})
        route.setdefault("telemetry", {"calls": 0, "duration_ms": 0, "input_tokens": 0, "output_tokens": 0, "cost_usd": 0.0})
        route.setdefault("mode", "change")
        route["routing"].setdefault("quality_control", "quality-control" in route.get("phases", []))
        route["schema_version"] = ROUTE_SCHEMA_VERSION
        changes.append(f"route schema migrated from {source} to {ROUTE_SCHEMA_VERSION}")
        route.setdefault("events", []).append({"event": "route-migrated", "at": utc_now(), "reason": changes[-1]})
    routing = route.setdefault("routing", {})
    if "maintainability_review" not in routing:
        routing["maintainability_review"] = False
        if source == ROUTE_SCHEMA_VERSION:
            changes.append("added default maintainability_review routing field")
    if "quality_control" not in routing:
        routing["quality_control"] = "quality-control" in route.get("phases", [])
        if source == ROUTE_SCHEMA_VERSION:
            changes.append("added default quality_control routing field")
    if "mode" not in route:
        route["mode"] = "change"
        if source == ROUTE_SCHEMA_VERSION:
            changes.append("added default change task mode")
    if source == ROUTE_SCHEMA_VERSION and changes:
        route.setdefault("events", []).append({"event": "route-normalized", "at": utc_now(), "reason": "; ".join(changes)})
    return route, changes


def apply_route_directives(route: dict[str, Any], metadata: dict[str, str], source_phase: str) -> list[str]:
    """Apply only safe additive route changes requested by validated phase evidence."""
    requested = list_value(metadata.get("route_add"))
    if metadata.get("risk_level") == "high":
        requested.extend(["design", "approval"])
    allowed = {"audit": {"design", "approval"}, "design": {"approval"}, "plan": {"approval"}}
    additions: list[str] = []
    reason = metadata.get("route_reason", f"{source_phase} evidence requested a safer route")
    for phase in dict.fromkeys(requested):
        if route.get("mode", "change") != "change" and phase in {"approval", "implement", "fix"}:
            continue
        if phase not in allowed.get(source_phase, set()) or phase in route["phases"]:
            continue
        anchor = "plan" if phase == "design" else "implement"
        route["phases"].insert(route["phases"].index(anchor), phase)
        route["phase_states"][phase] = {"status": "pending", "attempts": 0, "lanes": {"primary": {"status": "pending"}}}
        if phase == "approval" and phase not in route["human_gates"]:
            route["human_gates"].append(phase)
        route["routing"][phase] = True
        additions.append(phase)
    if additions:
        route.setdefault("events", []).append({
            "event": "route-changed", "at": utc_now(), "source_phase": source_phase,
            "added_phases": additions, "reason": reason,
        })
    return additions
