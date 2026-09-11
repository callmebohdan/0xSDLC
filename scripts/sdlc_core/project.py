"""Evidence-based AGENTS.md bootstrap drafting."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any


MANIFESTS = {
    "package.json": "Node.js", "pyproject.toml": "Python", "requirements.txt": "Python",
    "Cargo.toml": "Rust", "go.mod": "Go", "pom.xml": "Java/Maven", "build.gradle": "Java/Gradle",
    "CMakeLists.txt": "C++/CMake", "meson.build": "C++/Meson",
}

LANGUAGE_EXTENSIONS = {
    ".c": "C", ".cc": "C++", ".cpp": "C++", ".cxx": "C++",
    ".hh": "C++", ".hpp": "C++", ".hxx": "C++", ".ixx": "C++", ".cppm": "C++",
    ".py": "Python", ".js": "JavaScript", ".jsx": "JavaScript", ".ts": "TypeScript",
    ".tsx": "TypeScript", ".rs": "Rust", ".go": "Go", ".java": "Java",
}
STYLE_FILES = (
    ".clang-format", ".clang-tidy", "CPPLINT.cfg", ".editorconfig", "CONTRIBUTING.md",
    "CONTRIBUTING.rst", "pyproject.toml", "ruff.toml", "eslint.config.js", "eslint.config.mjs",
)
IGNORED_SCAN_DIRS = {".git", ".agents", ".venv", "venv", "node_modules", "vendor", "build", "dist", "out"}


def detect_languages(workspace: Path, limit: int = 1000) -> dict[str, int]:
    """Return bounded source-extension evidence without traversing generated trees."""
    counts: dict[str, int] = {}
    ambiguous_headers = 0
    inspected = 0
    for root, directories, files in os.walk(workspace):
        directories[:] = [name for name in directories if name not in IGNORED_SCAN_DIRS and not name.startswith(".")]
        for name in files:
            suffix = Path(name).suffix.lower()
            if suffix == ".h":
                ambiguous_headers += 1
            language = LANGUAGE_EXTENSIONS.get(suffix)
            if language:
                counts[language] = counts.get(language, 0) + 1
            inspected += 1
            if inspected >= limit:
                break
        if inspected >= limit:
            break
    if ambiguous_headers:
        owner = "C++" if "C++" in counts else "C" if "C" in counts else "C/C++ headers"
        counts[owner] = counts.get(owner, 0) + ambiguous_headers
    return dict(sorted(counts.items(), key=lambda item: (-item[1], item[0])))


def project_profile(workspace: Path) -> dict[str, Any]:
    readme = next((path for path in (workspace / "README.md", workspace / "README.rst", workspace / "README.txt") if path.is_file()), None)
    summary = "No README summary found."
    if readme:
        lines = [line.strip() for line in readme.read_text(encoding="utf-8", errors="replace").splitlines() if line.strip() and not line.startswith("#")]
        summary = " ".join(lines[:3])[:600] or summary
    manifests = [name for name in MANIFESTS if (workspace / name).is_file()]
    languages = detect_languages(workspace)
    style_files = [name for name in STYLE_FILES if (workspace / name).is_file()]
    top_level = sorted(path.name for path in workspace.iterdir() if not path.name.startswith(".") and path.name not in {"node_modules", "vendor"})[:30]
    commands: dict[str, str] = {}
    package_json = workspace / "package.json"
    if package_json.is_file():
        try:
            scripts = json.loads(package_json.read_text(encoding="utf-8")).get("scripts", {})
            commands.update({name: f"npm run {name}" for name in ("test", "lint", "build", "dev") if name in scripts})
        except json.JSONDecodeError:
            pass
    if (workspace / "pyproject.toml").is_file() or (workspace / "requirements.txt").is_file():
        commands.setdefault("test", "python -m pytest  # verify availability before running")
    return {
        "workspace": str(workspace), "summary": summary, "manifests": manifests,
        "ecosystems": sorted({MANIFESTS[name] for name in manifests}),
        "languages": languages, "style_files": style_files,
        "top_level": top_level, "commands": commands,
        "sources": [str(path.relative_to(workspace)) for path in [readme, *(workspace / name for name in manifests), *(workspace / name for name in style_files)] if path],
    }


def agents_draft(profile: dict[str, Any]) -> str:
    commands = "\n".join(f"- {name}: `{command}`" for name, command in profile["commands"].items()) or "- No commands established. Inspect project configuration before running or inventing commands."
    structure = "\n".join(f"- `{name}`" for name in profile["top_level"]) or "- No visible project entries found."
    sources = ", ".join(f"`{item}`" for item in profile["sources"]) or "none"
    languages = ", ".join(f"{name} ({count} files sampled)" for name, count in profile.get("languages", {}).items()) or "not established"
    style_files = ", ".join(f"`{name}`" for name in profile.get("style_files", [])) or "none detected"
    return f"""# Project instructions

> Generated draft. Review every inferred statement before adopting it. Evidence sources: {sources}.

## Mission

{profile['summary']}

## Detected environment

- Ecosystems: {', '.join(profile['ecosystems']) or 'not established'}
- Manifests: {', '.join(profile['manifests']) or 'none detected'}
- Languages: {languages}
- Style/tooling evidence: {style_files}

## Project commands

{commands}

## Repository structure

{structure}

## Working rules

- Read the task specification and nearest applicable instructions before editing.
- Inspect existing conventions before introducing a new pattern.
- Keep changes scoped and preserve unrelated user work.
- Run the narrowest relevant checks and report exact evidence and limitations.

## Engineering conventions

- Repository configuration and established local code take precedence over generic language guidance.
- Use detected formatter, linter, static-analysis, compiler-warning, and test configuration when available.
- Do not introduce a design pattern without a concrete problem, alternatives, and a testable benefit.
- Do not perform broad style cleanup as part of an unrelated task.

## Approval boundaries

- Ask before dependencies, CI/release configuration, public APIs, data migrations, destructive operations, secrets, or external side effects.
- Never expose credentials, weaken security or tests, or claim checks that were not run.

## Unresolved setup

- Confirm source and test directories, code style, required checks, Git/PR conventions, generated files, security constraints, and deployment ownership.
"""
