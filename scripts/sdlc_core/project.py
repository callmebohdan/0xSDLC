"""Evidence-based AGENTS.md bootstrap drafting."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


MANIFESTS = {
    "package.json": "Node.js", "pyproject.toml": "Python", "requirements.txt": "Python",
    "Cargo.toml": "Rust", "go.mod": "Go", "pom.xml": "Java/Maven", "build.gradle": "Java/Gradle",
}


def project_profile(workspace: Path) -> dict[str, Any]:
    readme = next((path for path in (workspace / "README.md", workspace / "README.rst", workspace / "README.txt") if path.is_file()), None)
    summary = "No README summary found."
    if readme:
        lines = [line.strip() for line in readme.read_text(encoding="utf-8", errors="replace").splitlines() if line.strip() and not line.startswith("#")]
        summary = " ".join(lines[:3])[:600] or summary
    manifests = [name for name in MANIFESTS if (workspace / name).is_file()]
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
        "top_level": top_level, "commands": commands,
        "sources": [str(path.relative_to(workspace)) for path in [readme, *(workspace / name for name in manifests)] if path],
    }


def agents_draft(profile: dict[str, Any]) -> str:
    commands = "\n".join(f"- {name}: `{command}`" for name, command in profile["commands"].items()) or "- No commands established. Inspect project configuration before running or inventing commands."
    structure = "\n".join(f"- `{name}`" for name in profile["top_level"]) or "- No visible project entries found."
    sources = ", ".join(f"`{item}`" for item in profile["sources"]) or "none"
    return f"""# Project instructions

> Generated draft. Review every inferred statement before adopting it. Evidence sources: {sources}.

## Mission

{profile['summary']}

## Detected environment

- Ecosystems: {', '.join(profile['ecosystems']) or 'not established'}
- Manifests: {', '.join(profile['manifests']) or 'none detected'}

## Project commands

{commands}

## Repository structure

{structure}

## Working rules

- Read the task specification and nearest applicable instructions before editing.
- Inspect existing conventions before introducing a new pattern.
- Keep changes scoped and preserve unrelated user work.
- Run the narrowest relevant checks and report exact evidence and limitations.

## Approval boundaries

- Ask before dependencies, CI/release configuration, public APIs, data migrations, destructive operations, secrets, or external side effects.
- Never expose credentials, weaken security or tests, or claim checks that were not run.

## Unresolved setup

- Confirm source and test directories, code style, required checks, Git/PR conventions, generated files, security constraints, and deployment ownership.
"""
