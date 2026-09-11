"""Dependency-free checks for the published JSON Schema contracts."""

from __future__ import annotations

from typing import Any

from .config import ROUTE_SCHEMA_VERSION


ROUTE_REQUIRED = {
    "schema_version", "task_id", "request", "workspace", "classification", "model",
    "status", "current_phase", "phases", "routing", "phase_states", "events", "created_at",
}


def validate_route(route: dict[str, Any]) -> None:
    missing = ROUTE_REQUIRED - route.keys()
    if missing:
        raise ValueError(f"route missing required field(s): {', '.join(sorted(missing))}")
    if route["schema_version"] != ROUTE_SCHEMA_VERSION:
        raise ValueError(f"route must be migrated to schema {ROUTE_SCHEMA_VERSION}")
    if route["classification"] not in {"small", "standard", "high-risk"}:
        raise ValueError("invalid route classification")
    if not isinstance(route["phases"], list) or not route["phases"]:
        raise ValueError("route phases must be a non-empty list")
    if route["current_phase"] not in route["phase_states"]:
        raise ValueError("current phase is absent from phase_states")
    routing = route["routing"]
    for field in ("design", "approval", "maintainability_review"):
        if not isinstance(routing.get(field), bool):
            raise ValueError(f"route routing.{field} must be boolean")
    for phase in route["phases"]:
        if phase not in route["phase_states"]:
            raise ValueError(f"phase has no state: {phase}")
