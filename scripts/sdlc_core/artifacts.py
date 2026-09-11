"""Artifact metadata parsing and backward-compatible validation."""

from __future__ import annotations

import re
from pathlib import Path

from .config import ARTIFACT_SCHEMA_VERSION, VALID_ARTIFACT_STATUS


SUPPORTED_ARTIFACT_SCHEMAS = {"0.1", ARTIFACT_SCHEMA_VERSION}


def parse_front_matter(path: Path) -> dict[str, str]:
    lines = path.read_text(encoding="utf-8").splitlines()
    if not lines or lines[0].strip() != "---":
        raise ValueError("missing YAML front matter")
    try:
        end = next(index for index, line in enumerate(lines[1:], 1) if line.strip() == "---")
    except StopIteration as exc:
        raise ValueError("unterminated YAML front matter") from exc
    result: dict[str, str] = {}
    for line in lines[1:end]:
        match = re.match(r"^([A-Za-z_][\w-]*):\s*(.*?)\s*$", line)
        if match:
            result[match.group(1)] = match.group(2).strip().strip('"\'')
    return result


def list_value(raw: str | None) -> list[str]:
    if not raw:
        return []
    return [item.strip().strip('"\'') for item in raw.strip("[]").split(",") if item.strip()]


def validate_artifact(path: Path, task_id: str, phase: str) -> dict[str, str]:
    metadata = parse_front_matter(path)
    schema = metadata.get("schema_version", "0.1")
    if schema not in SUPPORTED_ARTIFACT_SCHEMAS:
        raise ValueError(f"unsupported artifact schema {schema!r}; supported: {sorted(SUPPORTED_ARTIFACT_SCHEMAS)}")
    missing = [key for key in ("task_id", "phase", "status") if not metadata.get(key)]
    if missing:
        raise ValueError(f"missing required front-matter field(s): {', '.join(missing)}")
    if metadata["task_id"] != task_id:
        raise ValueError(f"task_id is {metadata['task_id']!r}, expected {task_id!r}")
    if metadata["phase"] != phase:
        raise ValueError(f"phase is {metadata['phase']!r}, expected {phase!r}")
    if metadata["status"] not in VALID_ARTIFACT_STATUS:
        raise ValueError(f"invalid artifact status {metadata['status']!r}")
    if metadata["status"] == "verified" and phase != "verify":
        raise ValueError("only verification artifacts may use status: verified")
    if phase == "review" and metadata.get("decision") not in {"approve", "fix", "needs-review"}:
        raise ValueError("review artifact requires decision: approve, fix, or needs-review")
    return metadata
