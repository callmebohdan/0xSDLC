"""Publish 0xSDLC contracts and portable provider skills in one rollout."""

from __future__ import annotations

import argparse
import os
import shutil
import sys
from pathlib import Path


SOURCE = Path(__file__).resolve().parents[1]
SKILLS_SOURCE = SOURCE / "support" / "skills"
CODEX_METADATA_SOURCE = SOURCE / "support" / "codex-skills"
SKILL_NAMES = ("0xsdlc-autopilot", "0xsdlc-agent", "0xsdlc-bootstrap")
PUBLISH_PATHS = [
    "AGENTS.md",
    "README.md",
    "docs",
    "support",
    "templates",
    "schemas",
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


def default_claude_skills() -> Path:
    return Path.home() / ".claude" / "skills"


def default_cursor_skills() -> Path:
    return Path.home() / ".cursor" / "skills"


def default_shared_skills() -> Path:
    return Path.home() / ".agents" / "skills"


def remove_published_path(path: Path, root: Path) -> None:
    """Remove one known published child without touching runtime sessions or siblings."""
    root = root.resolve()
    parent = path.parent.resolve()
    if parent != root and not parent.is_relative_to(root):
        raise ValueError(f"refusing to remove path outside publish root: {path}")
    if path.is_symlink() or (hasattr(path, "is_junction") and path.is_junction()):
        path.unlink()
    elif path.is_dir():
        shutil.rmtree(path)
    elif path.exists():
        path.unlink()


def install_skills(source_root: Path, target: Path, force: bool, *, codex_metadata: bool = False) -> None:
    target.mkdir(parents=True, exist_ok=True)
    for name in SKILL_NAMES:
        source = source_root / name
        destination = target / name
        if destination.exists() and not force:
            raise FileExistsError(f"skill already exists: {destination}")
        if force:
            remove_published_path(destination, target)
        shutil.copytree(source, destination)
        if codex_metadata:
            metadata = CODEX_METADATA_SOURCE / name / "agents"
            if metadata.is_dir():
                shutil.copytree(metadata, destination / "agents", dirs_exist_ok=True)


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
        help="deprecated alias for --codex-skills-dir",
    )
    parser.add_argument("--codex-skills-dir", type=Path, default=default_codex_skills())
    parser.add_argument("--claude-skills-dir", type=Path, default=default_claude_skills())
    parser.add_argument("--cursor-skills-dir", type=Path, default=default_cursor_skills())
    parser.add_argument("--shared-skills-dir", type=Path, default=default_shared_skills())
    parser.add_argument(
        "--skip-codex-skills",
        action="store_true",
        help="publish only the 0xSDLC runtime contracts",
    )
    parser.add_argument("--skip-provider-skills", action="store_true", help="publish contracts only; install no skill wrappers")
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
        if args.force:
            remove_published_path(destination, target)
        if source.is_dir():
            shutil.copytree(
                source,
                destination,
                ignore=shutil.ignore_patterns("__pycache__", "*.pyc"),
            )
        else:
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, destination)
    print(f"Installed 0xSDLC into {target}")
    if not args.skip_provider_skills:
        codex_target = (args.skills_dir or args.codex_skills_dir).expanduser().resolve()
        targets = [
            ("Claude Code", args.claude_skills_dir.expanduser().resolve(), False),
            ("Cursor", args.cursor_skills_dir.expanduser().resolve(), False),
            ("portable", args.shared_skills_dir.expanduser().resolve(), False),
        ]
        if not args.skip_codex_skills:
            targets.insert(0, ("Codex", codex_target, True))
        try:
            for label, skills_target, metadata in targets:
                install_skills(SKILLS_SOURCE, skills_target, args.force, codex_metadata=metadata)
                print(f"Installed 0xSDLC skills for {label} into {skills_target}")
        except FileExistsError as exc:
            print(f"Install stopped; {exc}. Re-run with --force to replace it.", file=sys.stderr)
            return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
