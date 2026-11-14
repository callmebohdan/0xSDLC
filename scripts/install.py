"""Publish 0xSDLC contracts and portable provider skills in one rollout."""

from __future__ import annotations

import argparse
import os
import shutil
import sys
import tempfile
from pathlib import Path


SOURCE = Path(__file__).resolve().parents[1]
SKILLS_SOURCE = SOURCE / "support" / "integrations" / "portable-skills"
CODEX_METADATA_SOURCE = SOURCE / "support" / "integrations" / "codex" / "metadata"
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
    config_dir = os.environ.get("CLAUDE_CONFIG_DIR")
    base = Path(config_dir).expanduser() if config_dir else Path.home() / ".claude"
    return base / "skills"


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


def _path_exists(path: Path) -> bool:
    return path.exists() or path.is_symlink() or (hasattr(path, "is_junction") and path.is_junction())


def preflight_install(runtime: Path, skill_targets: list[tuple[str, Path, bool]], upgrade: bool) -> list[Path]:
    """Check all collisions and sources before changing any published destination."""
    roots = [runtime, *(target for _, target, _ in skill_targets)]
    for index, left in enumerate(roots):
        if left == Path(left.anchor) or left == Path.home().resolve():
            raise ValueError(f"refusing to use a filesystem root or home directory as an install destination: {left}")
        if left == SOURCE or left.is_relative_to(SOURCE) or SOURCE.is_relative_to(left):
            raise ValueError(f"install target overlaps the source checkout: {left}")
        for right in roots[index + 1:]:
            if left == right or left.is_relative_to(right) or right.is_relative_to(left):
                raise ValueError(f"install destinations overlap: {left} and {right}")
        if _path_exists(left) and not left.is_dir():
            raise ValueError(f"install destination is not a directory: {left}")

    if any((parent / ".git").exists() for parent in (runtime, *runtime.parents)):
        raise ValueError(f"runtime destination must stay outside Git workspaces: {runtime}")
    missing_sources = [relative for relative in PUBLISH_PATHS if not _path_exists(SOURCE / relative)]
    missing_sources.extend(
        f"support/integrations/portable-skills/{name}"
        for name in SKILL_NAMES
        if not (SKILLS_SOURCE / name).is_dir()
    )
    if missing_sources:
        raise FileNotFoundError("installer source is incomplete: " + ", ".join(missing_sources))

    if _path_exists(runtime) and any(runtime.iterdir()) and not upgrade:
        raise FileExistsError(f"runtime destination is not empty (use --upgrade to replace managed paths): {runtime}")
    if not upgrade:
        conflicts = [
            target / name
            for _, target, _ in skill_targets
            for name in SKILL_NAMES
            if _path_exists(target / name)
        ]
        if conflicts:
            raise FileExistsError("0xSDLC skill paths already exist (use --upgrade to replace them): " + ", ".join(str(path) for path in conflicts))
    return roots


def stage_copy(source: Path, destination: Path, root: Path, stage_roots: list[Path], operations: list[dict[str, Path]]) -> None:
    stage_root = Path(tempfile.mkdtemp(prefix=".0xsdlc-stage-", dir=root))
    stage_roots.append(stage_root)
    staged = stage_root / "new"
    if source.is_dir():
        shutil.copytree(source, staged, ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
    else:
        shutil.copy2(source, staged)
    operations.append({"root": root, "destination": destination, "staged": staged, "backup": stage_root / "backup"})


class RollbackError(OSError):
    """An install rollback failed; staging directories contain recovery data."""


def apply_staged(operations: list[dict[str, Path]], stage_roots: list[Path]) -> None:
    committed: list[dict[str, Path | bool]] = []
    rollback_errors: list[str] = []
    preserve_stage_roots = False
    try:
        for operation in operations:
            destination = operation["destination"]
            backup = operation["backup"]
            had_destination = _path_exists(destination)
            if had_destination:
                os.replace(destination, backup)
            try:
                os.replace(operation["staged"], destination)
            except OSError:
                if had_destination:
                    try:
                        os.replace(backup, destination)
                    except OSError as exc:
                        rollback_errors.append(f"could not restore {destination} from {backup}: {exc}")
                raise
            committed.append({**operation, "had_destination": had_destination})
    except OSError:
        for operation in reversed(committed):
            destination = operation["destination"]
            try:
                remove_published_path(destination, operation["root"])
            except OSError as exc:
                rollback_errors.append(f"could not remove partially published {destination}: {exc}")
            if operation["had_destination"]:
                try:
                    os.replace(operation["backup"], destination)
                except OSError as exc:
                    rollback_errors.append(f"could not restore {destination} from {operation['backup']}: {exc}")
        if rollback_errors:
            preserve_stage_roots = True
            preserved = ", ".join(str(path) for path in stage_roots)
            details = "; ".join(rollback_errors)
            raise RollbackError(
                f"install failed and rollback was incomplete ({details}); recovery backups were preserved in: {preserved}"
            )
        raise
    finally:
        if not preserve_stage_roots:
            for stage_root in stage_roots:
                shutil.rmtree(stage_root, ignore_errors=True)


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
    parser.add_argument(
        "--portable-skills-dir",
        "--shared-skills-dir",
        dest="portable_skills_dir",
        type=Path,
        default=default_shared_skills(),
        help="portable skill directory (default: user-level .agents/skills)",
    )
    parser.add_argument(
        "--skip-codex-skills",
        action="store_true",
        help="publish only the 0xSDLC runtime contracts",
    )
    parser.add_argument("--skip-provider-skills", action="store_true", help="publish contracts only; install no skill wrappers")
    parser.add_argument(
        "--upgrade", "--force", dest="force", action="store_true",
        help="replace only published 0xSDLC paths and named skill folders; preserve sessions and sibling skills",
    )
    args = parser.parse_args()
    target = args.agents_dir.expanduser().resolve()
    skill_targets: list[tuple[str, Path, bool]] = []
    if not args.skip_provider_skills:
        codex_target = (args.skills_dir or args.codex_skills_dir).expanduser().resolve()
        skill_targets = [
            ("Claude Code", args.claude_skills_dir.expanduser().resolve(), False),
            ("Cursor", args.cursor_skills_dir.expanduser().resolve(), False),
            ("portable", args.portable_skills_dir.expanduser().resolve(), False),
        ]
        if not args.skip_codex_skills:
            skill_targets.insert(0, ("Codex", codex_target, True))
    stage_roots: list[Path] = []
    try:
        roots = preflight_install(target, skill_targets, args.force)
        for root in roots:
            root.mkdir(parents=True, exist_ok=True)
        operations: list[dict[str, Path]] = []
        for relative in PUBLISH_PATHS:
            stage_copy(SOURCE / relative, target / relative, target, stage_roots, operations)
        if not args.skip_provider_skills:
            for label, skills_target, codex_metadata in skill_targets:
                for name in SKILL_NAMES:
                    destination = skills_target / name
                    stage_copy(SKILLS_SOURCE / name, destination, skills_target, stage_roots, operations)
                    if codex_metadata:
                        metadata = CODEX_METADATA_SOURCE / name
                        if metadata.is_dir():
                            shutil.copytree(metadata, operations[-1]["staged"] / "agents", dirs_exist_ok=True)
        apply_staged(operations, stage_roots)
    except (FileExistsError, FileNotFoundError, OSError, ValueError) as exc:
        if not isinstance(exc, RollbackError):
            for stage_root in stage_roots:
                shutil.rmtree(stage_root, ignore_errors=True)
        print(f"Install stopped: {exc}", file=sys.stderr)
        return 2
    print(f"Installed 0xSDLC into {target}")
    for label, skills_target, _ in skill_targets:
        print(f"Installed 0xSDLC skills for {label} into {skills_target}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
