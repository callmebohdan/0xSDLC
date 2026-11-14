"""Durable call records and provider-neutral timing and usage summaries."""

from __future__ import annotations

import json
import math
import socket
import subprocess
import time
import uuid
from pathlib import Path
from typing import Any

from .storage import read_json, utc_now, write_json, write_text


TOKEN_FIELDS = ("input_tokens", "output_tokens", "cache_read_tokens", "cache_write_tokens", "reasoning_tokens")
USAGE_FIELDS = (*TOKEN_FIELDS, "cost_usd", "inference_ms")
TOTAL_FIELDS = ("duration_ms", *USAGE_FIELDS)


def elapsed_ms(start: float) -> int:
    return int((time.monotonic() - start) * 1000)


def commit_at(workspace: Path) -> str | None:
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--verify", "HEAD"], cwd=workspace, capture_output=True,
            text=True, check=False, timeout=3,
        )
    except (OSError, subprocess.TimeoutExpired):
        return None
    return (result.stdout.strip() or None) if result.returncode == 0 else None


def open_attempt(workspace: Path, source: str, model: str, started_at: str) -> dict[str, Any]:
    start = time.monotonic()
    attempt = {
        "attempt_id": uuid.uuid4().hex, "source": source, "provenance": "captured",
        "started_at": started_at, "finished_at": None, "duration_ms": None, "outcome": "running",
        "monotonic_start": start, "clock_origin": time.time() - start, "host": socket.gethostname(),
        "commit_start": commit_at(workspace), "commit_end": None, "call_ids": [], "artifacts": [],
    }
    if source == "native":
        attempt.update({
            "provider": None, "model": model if model != "native" else None,
            "adapter_wall_ms": None, "usage_source": None, "cost_source": None,
            **dict.fromkeys(USAGE_FIELDS),
        })
    return attempt


def close_attempt(attempt: dict[str, Any], workspace: Path, outcome: str, finished_at: str) -> None:
    duration = elapsed_ms(attempt["monotonic_start"])
    if attempt["host"] != socket.gethostname() or duration < 0:
        raise ValueError("phase clock is unavailable on this host; record an interruption instead")
    if attempt["source"] == "native" and abs(time.time() - time.monotonic() - attempt["clock_origin"]) > 2:
        raise ValueError("phase clock origin changed; record an interruption instead")
    attempt.update(outcome=outcome, finished_at=finished_at, duration_ms=duration, commit_end=commit_at(workspace))


def call_path(task_dir: Path, call_id: str) -> Path:
    if uuid.UUID(hex=call_id).hex != call_id:
        raise ValueError(f"invalid call ID: {call_id}")
    return task_dir / "calls" / f"{call_id}.json"


def prepare_call(
    task_dir: Path, attempt: dict[str, Any], phase: str, lane: str, model: str, artifact: str,
) -> dict[str, Any]:
    call_id = uuid.uuid4().hex
    base = f"attempts/{attempt['attempt_id']}/{call_id}"
    label = phase if lane == "primary" else f"{phase}-{lane}"
    event = {
        "call_id": call_id, "attempt_id": attempt["attempt_id"], "phase": phase, "lane": lane,
        "adapter": model, "model": None, "provider": None, "outcome": "pending", "source": "adapter",
        "provenance": "captured", "started_at": None, "finished_at": None, "exit_code": None,
        "commit_start": attempt["commit_start"], "cost_source": None, "usage_source": None,
        "telemetry_sidecar": f"{base}/adapter-{label}.telemetry.json",
        "evidence": {
            "prompt": f"{base}/prompt-{label}.md", "stdout": f"{base}/adapter-{label}.stdout.txt",
            "stderr": f"{base}/adapter-{label}.stderr.txt", "artifact": artifact,
        },
        **dict.fromkeys(TOTAL_FIELDS),
    }
    write_json(call_path(task_dir, call_id), event)
    attempt["call_ids"].append(call_id)
    return event


def start_call(task_dir: Path, event: dict[str, Any], provider: str) -> None:
    event.update(started_at=utc_now(), provider=provider if provider != "generic" else None, outcome="running")
    write_json(call_path(task_dir, event["call_id"]), event)


def provider_usage(task_dir: Path, event: dict[str, Any]) -> None:
    relative = event.get("telemetry_sidecar")
    if not relative or not (task_dir / relative).is_file():
        return
    try:
        usage = read_json(task_dir / relative)
        if not isinstance(usage, dict) or usage.get("call_id") != event["call_id"]:
            event["telemetry_warning"] = "provider sidecar does not match call ID"
            return
        for field in USAGE_FIELDS:
            value = usage.get(field)
            if type(value) is int and value >= 0:
                event[field] = value
            elif field not in TOKEN_FIELDS and type(value) is float and math.isfinite(value) and value >= 0:
                event[field] = value
        for field in ("provider", "model"):
            if isinstance(usage.get(field), str) and usage[field].strip():
                event[field] = usage[field]
        if any(event[field] is not None for field in USAGE_FIELDS):
            event["usage_source"] = "provider-sidecar"
        if event["cost_usd"] is not None:
            source = usage.get("cost_source")
            event["cost_source"] = source if isinstance(source, str) and source.strip() else "provider-sidecar"
    except (OSError, UnicodeError, ValueError):
        event["telemetry_warning"] = "invalid provider sidecar"


def persist_result(task_dir: Path, event: dict[str, Any]) -> None:
    path = call_path(task_dir, event["call_id"])
    if path.is_file() and read_json(path)["outcome"] not in {"pending", "running"}:
        return
    provider_usage(task_dir, event)
    write_json(path, event)


def summarize(calls: list[dict[str, Any]]) -> dict[str, Any]:
    summary: dict[str, Any] = {"calls": len(calls), "coverage": {}}
    for field in TOTAL_FIELDS:
        known = [call[field] for call in calls if call.get(field) is not None]
        summary[field] = sum(known) if known else None
        summary["coverage"][field] = len(known)
    return summary


def sync_metrics(task_dir: Path, route: dict[str, Any], *, recover: bool = False) -> bool:
    """Project the atomic call journals into JSONL and the route summary under the task lock."""
    calls = []
    for path in (task_dir / "calls").glob("*.json"):
        event = read_json(path)
        if event["outcome"] in {"pending", "running"}:
            if not recover:
                continue
            outcome = "interrupted" if event["outcome"] == "running" else "not-started"
            event.update(outcome=outcome, provenance="retrospective", recovered_at=utc_now())
            write_json(path, event)
        calls.append(event)
    calls.sort(key=lambda event: (event["started_at"] or event.get("recovered_at", ""), event["call_id"]))
    path = task_dir / "metrics.jsonl"
    existing = path.read_text(encoding="utf-8") if path.is_file() else ""
    legacy = [line for line in existing.splitlines() if line.strip() and "call_id" not in json.loads(line)]
    lines = legacy + [json.dumps(event, sort_keys=True, allow_nan=False) for event in calls]
    rendered = "\n".join(lines) + "\n" if lines else ""
    if rendered != existing:
        write_text(path, rendered)
    summary = summarize([call for call in calls if call["outcome"] != "not-started"])
    previous = route.get("telemetry")
    if previous and "coverage" not in previous:
        route.setdefault("legacy_telemetry", previous)
    changed = summary != previous
    route["telemetry"] = summary
    if recover:
        by_id = {event["call_id"]: event for event in calls}
        for state in route["phase_states"].values():
            for lane in state.get("lanes", {}).values():
                call = by_id.get(lane.get("call_id"))
                if call and lane.get("status") == "interrupted" and (call["outcome"] != "interrupted" or lane.get("exit_code") != call["exit_code"]):
                    lane.update(status=call["outcome"], exit_code=call["exit_code"])
                    changed = True
    return changed


def record(task_dir: Path, route: dict[str, Any], event: dict[str, Any]) -> None:
    """Record a completed call; replay the same call ID to make a retry idempotent."""
    event = {
        **dict.fromkeys(TOTAL_FIELDS), "call_id": uuid.uuid4().hex, "started_at": None,
        "finished_at": utc_now(), "outcome": "succeeded" if event.get("exit_code", 0) == 0 else "failed",
        "source": "adapter", "provenance": "captured", "cost_source": None, "usage_source": None, **event,
    }
    persist_result(task_dir, event)
    sync_metrics(task_dir, route)
