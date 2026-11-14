"""Atomic task persistence, locking, and interrupted-run recovery."""

from __future__ import annotations

import datetime as dt
import errno
import json
import os
import socket
import uuid
from pathlib import Path
from typing import Any, BinaryIO


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


def check_session_writable(path: Path) -> None:
    probe = path / f".0xsdlc-write-probe-{uuid.uuid4().hex}"
    try:
        write_text(probe, "create")
        write_text(probe, "replace")
        probe.unlink()
    except OSError as exc:
        raise OSError(
            f"cannot create and atomically replace session files in {path}: {exc}. "
            "Choose a writable, Git-ignored path with --sessions-root or "
            "0XSDLC_SESSIONS_ROOT. For an existing session, use its writable directory."
        ) from exc


def process_is_alive(pid: int) -> bool:
    if os.name == "nt":
        import ctypes
        from ctypes import wintypes

        kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
        open_process = kernel32.OpenProcess
        open_process.argtypes = (wintypes.DWORD, wintypes.BOOL, wintypes.DWORD)
        open_process.restype = wintypes.HANDLE
        handle = open_process(0x00100000, False, pid)  # SYNCHRONIZE
        if not handle:
            return ctypes.get_last_error() != 87  # ERROR_INVALID_PARAMETER: PID does not exist
        wait = kernel32.WaitForSingleObject
        wait.argtypes = (wintypes.HANDLE, wintypes.DWORD)
        wait.restype = wintypes.DWORD
        close_handle = kernel32.CloseHandle
        close_handle.argtypes = (wintypes.HANDLE,)
        try:
            return wait(handle, 0) != 0  # WAIT_OBJECT_0: process exited
        finally:
            close_handle(handle)
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    except (PermissionError, OverflowError):
        pass
    return True


def lock_file(handle: BinaryIO) -> None:
    if os.name == "nt":
        import msvcrt

        handle.seek(0)
        msvcrt.locking(handle.fileno(), msvcrt.LK_NBLCK, 1)
    else:
        import fcntl

        fcntl.flock(handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)


class TaskLock:
    """Hold an OS lock until the handle closes, including on process exit."""

    def __init__(self, task_dir: Path, stale_seconds: int = 1800) -> None:
        self.path = task_dir / ".0xsdlc.lock"
        self.guard = task_dir / ".0xsdlc.guard"
        self.stale_seconds = stale_seconds
        self.handle: BinaryIO | None = None

    def check_previous_marker(self) -> None:
        try:
            owner = read_json(self.path)
        except FileNotFoundError:
            return
        except (UnicodeError, ValueError) as exc:
            raise RuntimeError(f"unreadable legacy task lock: {self.path}") from exc
        if isinstance(owner, dict) and owner.get("guarded") is True:
            return
        pid = owner.get("pid") if isinstance(owner, dict) else None
        if (
            type(pid) is not int or not 0 < pid < 2**31 or owner.get("host") != socket.gethostname()
            or dt.datetime.now().timestamp() - self.path.stat().st_mtime <= self.stale_seconds
            or process_is_alive(pid)
        ):
            raise RuntimeError(f"cannot recover legacy task lock: {self.path}; verify its owner has exited")

    def __enter__(self) -> "TaskLock":
        self.path.parent.mkdir(parents=True, exist_ok=True)
        # Keep the guard file so every contender locks the same file, even across restarts.
        handle = self.guard.open("a+b")
        try:
            try:
                lock_file(handle)
            except OSError as exc:
                if exc.errno in {errno.EACCES, errno.EAGAIN, errno.EDEADLK}:
                    raise RuntimeError(f"task is locked by another run: {self.path.parent}") from exc
                raise
            self.check_previous_marker()
            payload = {"pid": os.getpid(), "host": socket.gethostname(), "acquired_at": utc_now(), "guarded": True}
            write_json(self.path, payload)
        except BaseException:
            handle.close()
            raise
        self.handle = handle
        return self

    def __exit__(self, *_: object) -> None:
        if self.handle is not None:
            try:
                self.path.unlink(missing_ok=True)
            finally:
                self.handle.close()
                self.handle = None


def recover_interrupted(route: dict[str, Any]) -> bool:
    """Convert orphaned running phases into retryable blocked state."""
    recovered = False
    for phase, state in route.get("phase_states", {}).items():
        if state.get("status") == "running":
            now = utc_now()
            state.update({"status": "blocked", "finished_at": None, "reason": "previous run interrupted"})
            for lane in state.get("lanes", {}).values():
                if lane.get("status") == "running":
                    lane["status"] = "interrupted"
            for attempt in state.get("attempt_history", []):
                if attempt["outcome"] == "running":
                    attempt.update(outcome="interrupted", recovered_at=now, provenance="retrospective")
            route.setdefault("events", []).append({
                "event": "run-interrupted", "phase": phase, "at": now,
                "attempt_id": state.get("attempt_id"), "started_at": state.get("started_at"),
                "finished_at": None, "provenance": "retrospective",
                "reason": "phase was still running when the task was reopened",
            })
            recovered = True
    if recovered:
        route["status"] = "blocked"
    return recovered
