"""Provider capability profiles and command resolution."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

from .config import library_path


REQUIRED_PROFILE_FIELDS = {"schema_version", "name", "command_env", "capabilities", "skill_locations"}


def profile_path(name: str) -> Path:
    return library_path(f"support/adapters/profiles/{name}.json")


def load_profile(name: str) -> dict[str, Any]:
    path = profile_path(name)
    if not path.is_file() and name not in {"generic", "codex", "claude", "cursor"}:
        path = profile_path("generic")
    profile = json.loads(path.read_text(encoding="utf-8"))
    missing = REQUIRED_PROFILE_FIELDS - profile.keys()
    if missing:
        raise ValueError(f"provider profile {path} missing: {', '.join(sorted(missing))}")
    return profile


def configured(name: str) -> bool:
    return bool(os.environ.get(load_profile(name)["command_env"]))


def select_model(requested: str) -> str:
    if requested != "auto":
        load_profile(requested)
        return requested
    for name in ("codex", "claude", "cursor", "generic"):
        if configured(name):
            return name
    return "generic"


def adapter_command(name: str) -> str | None:
    return os.environ.get(load_profile(name)["command_env"])


def validate_profiles() -> list[str]:
    errors: list[str] = []
    for name in ("generic", "codex", "claude", "cursor"):
        try:
            profile = load_profile(name)
            for capability in ("prompt_file", "workspace", "artifact_output"):
                if capability not in profile["capabilities"]:
                    errors.append(f"{name}: missing capability declaration {capability}")
        except (OSError, ValueError, json.JSONDecodeError) as exc:
            errors.append(f"{name}: {exc}")
    return errors
