"""Publish 0xSDLC contracts and Codex chat skills in one rollout."""

from __future__ import annotations

import argparse
import os
import shutil
import sys
from pathlib import Path


SOURCE = Path(__file__).resolve().parents[1]
CODEX_SKILLS_SOURCE = SOURCE / "support" / "codex-skills"
PUBLISH_PATHS = [
    "AGENTS.md",
    "README.md",
    "docs",
    "support",
    "templates",
    "scripts",
    "coding-standards",
    "0xSDLC-autopilot",
    "0xSDLC-design",
    "0xSDLC-fix",
    "0xSDLC-implement",
    "0xSDLC-plan",
    "0xSDLC-verify",
    "orchestrator",
    "run-instructions",
]


def default_system_agents() -> Path:
    override = os.environ.get("0XSDLC_AGENTS_HOME")
    if override:
        return Path(override).expanduser()
    if os.name == "nt":
        user_root = Path(os.environ.get("USERPROFILE", str(Path.home())))
        return user_root / ".agents" / "0xsdlc"
    return Path.home() / ".agents" / "0xsdlc"


def default_codex_skills() -> Path:
    override = os.environ.get("CODEX_HOME")
    if override:
        return Path(override).expanduser() / "skills"
    return Path.home() / ".codex" / "skills"


def main() -> int:
    parser = argparse.ArgumentParser(description="Publish 0xSDLC contracts to the user-level agent directory")
    parser.add_argument(
        "--agents-dir",
        type=Path,
        default=default_system_agents(),
        help="contract directory (default: user-level .agents/0xsdlc)",
    )
    parser.add_argument(
        "--skills-dir",
        type=Path,
        default=default_codex_skills(),
        help="Codex skill directory (default: user-level .codex/skills)",
    )
    parser.add_argument(
        "--skip-codex-skills",
        action="store_true",
        help="publish only the 0xSDLC runtime contracts",
    )
    parser.add_argument("--force", action="store_true", help="replace existing harness files")
    args = parser.parse_args()
    target = args.agents_dir.expanduser().resolve()
    target.mkdir(parents=True, exist_ok=True)
    if any(target.iterdir()) and not args.force:
        print("Install stopped; existing paths found:", file=sys.stderr)
        print(f"- {target}", file=sys.stderr)
        print("Re-run with --force only after reviewing those paths.", file=sys.stderr)
        return 2
    for relative in PUBLISH_PATHS:
        source = SOURCE / relative
        destination = target / relative
        if source.is_dir():
            shutil.copytree(
                source,
                destination,
                dirs_exist_ok=True,
                ignore=shutil.ignore_patterns("__pycache__", "*.pyc"),
            )
        else:
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, destination)
    print(f"Installed 0xSDLC into {target}")
    if not args.skip_codex_skills:
        skills_target = args.skills_dir.expanduser().resolve()
        skills_target.mkdir(parents=True, exist_ok=True)
        for name in ("0xsdlc-autopilot", "0xsdlc-agent"):
            source = CODEX_SKILLS_SOURCE / name
            destination = skills_target / name
            if destination.exists() and not args.force:
                print(
                    f"Codex skill already exists: {destination}. Re-run with --force to replace it.",
                    file=sys.stderr,
                )
                return 2
            shutil.copytree(source, destination, dirs_exist_ok=True)
        print(f"Installed 0xSDLC chat skills into {skills_target}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
