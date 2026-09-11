"""Atomic task persistence, locking, and interrupted-run recovery."""

from __future__ import annotations

import datetime as dt
import json
import os
import socket
import uuid
from pathlib import Path
from typing import Any


def utc_now() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat()


def write_text(path: Path, content: str, *, backup: bool = False) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.{uuid.uuid4().hex}.tmp")
    try:
        temporary.write_text(content.rstrip() + "\n", encoding="utf-8")
        if backup and path.exists():
            backup_path = path.with_suffix(path.suffix + ".bak")
            backup_path.write_bytes(path.read_bytes())
        temporary.replace(path)
    finally:
        if temporary.exists():
            temporary.unlink()


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, value: dict[str, Any], *, backup: bool = False) -> None:
    write_text(path, json.dumps(value, indent=2), backup=backup)


class TaskLock:
    """Portable exclusive lock with an explicit stale-lock recovery policy."""

    def __init__(self, task_dir: Path, stale_seconds: int = 1800) -> None:
        self.path = task_dir / ".0xsdlc.lock"
        self.stale_seconds = stale_seconds
        self.acquired = False

    def __enter__(self) -> "TaskLock":
        self.path.parent.mkdir(parents=True, exist_ok=True)
        if self.path.exists():
            age = dt.datetime.now().timestamp() - self.path.stat().st_mtime
            if age <= self.stale_seconds:
                owner = self.path.read_text(encoding="utf-8", errors="replace").strip()
                raise RuntimeError(f"task is locked by another run: {owner}")
            self.path.unlink()
        payload = json.dumps({"pid": os.getpid(), "host": socket.gethostname(), "acquired_at": utc_now()})
        try:
            with self.path.open("x", encoding="utf-8") as handle:
                handle.write(payload)
        except FileExistsError as exc:
            raise RuntimeError("task was locked concurrently") from exc
        self.acquired = True
        return self

    def __exit__(self, *_: object) -> None:
        if self.acquired and self.path.exists():
            self.path.unlink()
        self.acquired = False


def recover_interrupted(route: dict[str, Any]) -> bool:
    """Convert orphaned running phases into retryable blocked state."""
    recovered = False
    for phase, state in route.get("phase_states", {}).items():
        if state.get("status") == "running":
            state.update({"status": "blocked", "finished_at": utc_now(), "reason": "previous run interrupted"})
            route.setdefault("events", []).append({
                "event": "run-interrupted", "phase": phase, "at": utc_now(),
                "reason": "phase was still running when the task was reopened",
            })
            recovered = True
    if recovered:
        route["status"] = "blocked"
    return recovered
