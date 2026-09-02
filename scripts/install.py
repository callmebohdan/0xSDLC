"""Publish 0xSDLC contracts and portable provider skills in one rollout."""

from __future__ import annotations

import argparse
import os
import shutil
import sys
from pathlib import Path


SOURCE = Path(__file__).resolve().parents[1]
PORTABLE_SKILLS_SOURCE = SOURCE / "support" / "integrations" / "portable-skills"
CODEX_METADATA_SOURCE = SOURCE / "support" / "integrations" / "codex" / "metadata"
SKILL_NAMES = ("0xsdlc-autopilot", "0xsdlc-agent")
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
]

# Paths from pre-0.2 layouts. They are removed only from the explicitly selected
# 0xSDLC installation target during --force; repository files are never touched.
OBSOLETE_PATHS = [
    "support/0xSDLC-audit",
    "support/0xSDLC-intake",
    "support/0xSDLC-quality",
    "support/0xSDLC-review",
    "support/0xSDLC-spec",
    "support/0xSDLC-test",
    "support/0xSDLC-conventions",
    "support/codex-skills",
    "run-instructions",
    "templates/tasks.md",
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


def default_claude_skills() -> Path:
    override = os.environ.get("CLAUDE_CONFIG_DIR")
    return (Path(override).expanduser() if override else Path.home() / ".claude") / "skills"


def default_cursor_skills() -> Path:
    override = os.environ.get("CURSOR_CONFIG_DIR")
    return (Path(override).expanduser() if override else Path.home() / ".cursor") / "skills"


def default_portable_skills() -> Path:
    return Path.home() / ".agents" / "skills"


def main() -> int:
    parser = argparse.ArgumentParser(description="Publish 0xSDLC contracts to the user-level agent directory")
    parser.add_argument(
        "--agents-dir",
        type=Path,
        default=default_system_agents(),
        help="contract directory (default: user-level .agents/0xsdlc)",
    )
    parser.add_argument(
        "--codex-skills-dir",
        "--skills-dir",
        type=Path,
        dest="codex_skills_dir",
        default=default_codex_skills(),
        help="Codex skill directory (default: user-level .codex/skills; --skills-dir is a compatibility alias)",
    )
    parser.add_argument(
        "--claude-skills-dir",
        type=Path,
        default=default_claude_skills(),
        help="Claude Code skill directory (default: user-level .claude/skills)",
    )
    parser.add_argument(
        "--cursor-skills-dir",
        type=Path,
        default=default_cursor_skills(),
        help="Cursor skill directory (default: user-level .cursor/skills)",
    )
    parser.add_argument(
        "--portable-skills-dir",
        type=Path,
        default=default_portable_skills(),
        help="portable/Cursor-compatible skill directory (default: user-level .agents/skills)",
    )
    parser.add_argument(
        "--skip-provider-skills",
        "--skip-codex-skills",
        dest="skip_provider_skills",
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
    if args.force:
        for relative in OBSOLETE_PATHS:
            stale = target / relative
            if stale.is_dir():
                shutil.rmtree(stale)
            elif stale.is_file() or stale.is_symlink():
                stale.unlink()
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
    if not args.skip_provider_skills:
        skill_targets = (
            ("Codex", args.codex_skills_dir),
            ("Claude Code", args.claude_skills_dir),
            ("Cursor", args.cursor_skills_dir),
            ("portable", args.portable_skills_dir),
        )
        for label, target_value in skill_targets:
            skills_target = target_value.expanduser().resolve()
            skills_target.mkdir(parents=True, exist_ok=True)
            for name in SKILL_NAMES:
                source = PORTABLE_SKILLS_SOURCE / name
                destination = skills_target / name
                if destination.exists() and not args.force:
                    print(
                        f"{label} skill already exists: {destination}. Re-run with --force to replace it.",
                        file=sys.stderr,
                    )
                    return 2
                shutil.copytree(source, destination, dirs_exist_ok=True)
                if label == "Codex":
                    metadata_source = CODEX_METADATA_SOURCE / name
                    metadata_target = destination / "agents"
                    shutil.copytree(metadata_source, metadata_target, dirs_exist_ok=True)
            print(f"Installed 0xSDLC skills for {label} into {skills_target}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
