"""Canonical human-facing entry point for the 0xSDLC CLI."""

from __future__ import annotations

import sys
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from sdlc_core.artifacts import parse_front_matter, validate_artifact
from sdlc_core.cli import build_parser, main, now_id, slugify
from sdlc_core.providers import validate_profiles
from sdlc_core.routing import classify, migrate_route, needs_design, route_for, route_payload
from sdlc_core.runner import review_decision, run_full_cycle, run_phase, transition
from sdlc_core.storage import TaskLock, recover_interrupted, write_text


if __name__ == "__main__":
    raise SystemExit(main())
