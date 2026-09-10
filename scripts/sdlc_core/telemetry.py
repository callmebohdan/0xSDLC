"""Local, provider-neutral cost and latency records."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .storage import utc_now, write_text


NUMERIC_FIELDS = ("input_tokens", "output_tokens", "cost_usd")


def record(task_dir: Path, route: dict[str, Any], event: dict[str, Any]) -> None:
    event = {"at": utc_now(), **event}
    sidecar = task_dir / str(event.get("telemetry_sidecar", ""))
    if sidecar.is_file():
        try:
            provider = json.loads(sidecar.read_text(encoding="utf-8"))
            for field in NUMERIC_FIELDS:
                if isinstance(provider.get(field), (int, float)):
                    event[field] = provider[field]
        except (OSError, json.JSONDecodeError):
            event["telemetry_warning"] = "invalid provider sidecar"
    path = task_dir / "metrics.jsonl"
    existing = path.read_text(encoding="utf-8") if path.exists() else ""
    write_text(path, existing + json.dumps(event, sort_keys=True))
    summary = route.setdefault("telemetry", {"calls": 0, "duration_ms": 0, "input_tokens": 0, "output_tokens": 0, "cost_usd": 0.0})
    summary["calls"] += 1
    summary["duration_ms"] += int(event.get("duration_ms", 0))
    for field in NUMERIC_FIELDS:
        summary[field] += event.get(field, 0)
