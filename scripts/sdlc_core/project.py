"""Evidence-based project profile, readiness assessment, and AGENTS.md drafting."""

from __future__ import annotations

import hashlib
import json
import os
import re
import subprocess
from pathlib import Path
from typing import Any


MANIFESTS = {
    "package.json": "Node.js", "pyproject.toml": "Python", "requirements.txt": "Python",
    "Cargo.toml": "Rust", "go.mod": "Go", "pom.xml": "Java/Maven", "build.gradle": "Java/Gradle",
    "build.gradle.kts": "Java/Gradle", "CMakeLists.txt": "C++/CMake", "meson.build": "C++/Meson",
}

LANGUAGE_EXTENSIONS = {
    ".c": "C", ".cc": "C++", ".cpp": "C++", ".cxx": "C++",
    ".hh": "C++", ".hpp": "C++", ".hxx": "C++", ".ixx": "C++", ".cppm": "C++",
    ".py": "Python", ".js": "JavaScript", ".jsx": "JavaScript", ".ts": "TypeScript",
    ".tsx": "TypeScript", ".rs": "Rust", ".go": "Go", ".java": "Java",
}
STYLE_FILES = (
    ".clang-format", ".clang-tidy", "CPPLINT.cfg", ".editorconfig", "CONTRIBUTING.md",
    "CONTRIBUTING.rst", "ruff.toml", "eslint.config.js", "eslint.config.mjs",
)
IGNORED_SCAN_DIRS = {".git", ".agents", ".venv", "venv", "node_modules", "vendor", "build", "dist", "out"}
COMMAND_NAMES = ("test", "lint", "typecheck", "check", "build", "format", "dev")


def current_git_branch(workspace: Path) -> str | None:
    """Return the checked-out branch name, or None outside a named Git branch."""
    try:
        result = subprocess.run(
            ["git", "-C", str(workspace), "branch", "--show-current"],
            capture_output=True, text=True, check=False, timeout=3,
        )
    except (OSError, subprocess.TimeoutExpired):
        return None
    branch = result.stdout.strip()
    return branch if result.returncode == 0 and branch else None


def detect_languages(workspace: Path, limit: int = 1000) -> dict[str, int]:
    """Return bounded source-extension evidence without traversing generated trees."""
    counts: dict[str, int] = {}
    ambiguous_headers = 0
    inspected = 0
    for _, directories, files in os.walk(workspace):
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


def _read_limited(path: Path, limit: int = 65536) -> str:
    try:
        with path.open("r", encoding="utf-8", errors="replace") as stream:
            return stream.read(limit)
    except OSError:
        return ""


def _make_targets(path: Path) -> list[str]:
    text = _read_limited(path)
    return list(dict.fromkeys(re.findall(r"(?m)^([A-Za-z0-9_.-]+)\s*:(?![=])", text)))


def _ci_commands(text: str) -> list[str]:
    commands: list[str] = []
    block_indent: int | None = None
    for line in text.splitlines():
        match = re.match(r"^(\s*)(?:run|script|sh):\s*(.*?)\s*$", line)
        if match:
            indent, value = len(match.group(1)), match.group(2).strip()
            block_indent = indent if value in {"", "|", ">"} else None
            if value and value not in {"|", ">"}:
                commands.append(value.strip("'\""))
            continue
        if block_indent is None:
            continue
        indent = len(line) - len(line.lstrip())
        if line.strip() and indent <= block_indent:
            block_indent = None
        elif line.strip():
            value = re.sub(r"^\s*-\s*", "", line).strip()
            if value:
                commands.append(value)
    redacted = [
        re.sub(r"(?i)(\b(?:token|password|secret|api[_-]?key)\s*[:=]\s*)\S+", r"\1<redacted>", value)
        for value in commands
    ]
    return list(dict.fromkeys(redacted))[:30]


def _ci_profile(workspace: Path) -> tuple[list[dict[str, Any]], list[str]]:
    workflows = sorted((workspace / ".github" / "workflows").glob("*.y*ml"))[:12]
    workflows.extend(path for path in (
        workspace / ".gitlab-ci.yml", workspace / ".gitlab-ci.yaml",
        workspace / "azure-pipelines.yml", workspace / "Jenkinsfile",
        workspace / ".circleci" / "config.yml", workspace / ".buildkite" / "pipeline.yml",
    ) if path.is_file())
    entries: list[dict[str, Any]] = []
    for path in workflows:
        text = _read_limited(path)
        jobs = re.findall(r"(?m)^\s{2}([A-Za-z0-9_-]+):\s*(?:#.*)?$", text)
        entries.append({"path": path.relative_to(workspace).as_posix(), "jobs": list(dict.fromkeys(jobs)), "commands": _ci_commands(text)})
    return entries, [entry["path"] for entry in entries]


def assess_agents(existing: str | None, profile: dict[str, Any], source_hash: str | None = None) -> dict[str, Any]:
    """Find concrete gaps that block AGENTS.md from serving as project guidance."""
    if existing is None:
        return {"status": "missing", "findings": ["AGENTS.md is missing."], "sha256": None, "characters": 0}

    text = existing.strip()
    lowered = text.lower()
    findings: list[str] = []
    if len(text) < 200:
        findings.append("AGENTS.md is very short and may not give an agent enough project-specific direction.")
    if re.search(r"\b(todo|tbd|fill this|replace me|unresolved setup)\b", lowered):
        findings.append("AGENTS.md contains unresolved placeholders or setup items.")

    commands = profile["commands"]
    for name in ("test", "build", "lint", "typecheck", "format", "check"):
        command = commands.get(name)
        if not command:
            continue
        parts = command.lower().split()
        if parts[0] == "ctest":
            signature = "ctest"
        else:
            signature = " ".join(parts[:3] if parts[:2] in (["npm", "run"], ["python", "-m"]) else parts[:2])
        if signature and signature not in lowered:
            findings.append(f"The detected `{command}` {name} command is not documented in AGENTS.md.")
    if not commands and not re.search(r"\b(test|build|lint|check|verify)\b", lowered):
        findings.append("AGENTS.md does not explain how to verify changes or where to find verification guidance.")
    if profile["test_paths"] and not re.search(r"\b(test|tests|testing)\b", lowered):
        findings.append("Test directories exist, but AGENTS.md does not point agents to them.")

    if profile["ci_workflows"] and not re.search(r"\b(ci|continuous integration|github actions|workflow)\b", lowered):
        findings.append("CI workflows exist, but AGENTS.md does not point agents to their checks.")
    if profile["style_files"] and not re.search(r"\b(format|style|lint|contribut|convention)\b", lowered):
        findings.append("Formatting or contribution conventions exist, but AGENTS.md does not tell agents to follow them.")

    findings = list(dict.fromkeys(findings))
    return {
        "status": "ready" if not findings else "inadequate",
        "findings": findings,
        "sha256": source_hash or hashlib.sha256(existing.encode("utf-8")).hexdigest(),
        "characters": len(existing),
    }


def project_profile(workspace: Path) -> dict[str, Any]:
    readme = next((path for path in (workspace / "README.md", workspace / "README.rst", workspace / "README.txt") if path.is_file()), None)
    summary = "No README summary found."
    if readme:
        lines = [line.strip() for line in readme.read_text(encoding="utf-8", errors="replace").splitlines() if line.strip() and not line.startswith("#")]
        summary = " ".join(lines[:3])[:600] or summary
    manifests = [name for name in MANIFESTS if (workspace / name).is_file()]
    languages = detect_languages(workspace)
    style_files = [name for name in STYLE_FILES if (workspace / name).is_file()]
    if (workspace / "pyproject.toml").is_file() and re.search(
        r"(?m)^\s*\[tool\.(?:ruff|black|mypy|pyright|isort)(?:\.|\])",
        _read_limited(workspace / "pyproject.toml"),
    ):
        style_files.append("pyproject.toml")
    top_level = sorted(path.name for path in workspace.iterdir() if not path.name.startswith(".") and path.name not in {"node_modules", "vendor"})[:30]
    commands: dict[str, str] = {}
    package_json = workspace / "package.json"
    if package_json.is_file():
        try:
            scripts = json.loads(_read_limited(package_json)).get("scripts", {})
            commands.update({name: f"npm run {name}" for name in COMMAND_NAMES if name in scripts})
        except (json.JSONDecodeError, AttributeError):
            pass
    makefile = next((workspace / name for name in ("Makefile", "makefile", "GNUmakefile") if (workspace / name).is_file()), None)
    if makefile:
        targets = _make_targets(makefile)
        for name in COMMAND_NAMES:
            if name in targets:
                commands.setdefault(name, f"make {name}")
    if (workspace / "pyproject.toml").is_file():
        pyproject = _read_limited(workspace / "pyproject.toml")
        for name in ("pytest", "tox", "nox", "ruff"):
            if re.search(rf"(?m)^\s*\[tool\.{name}(?:\.|\])", pyproject):
                command = {"pytest": "python -m pytest", "tox": "tox", "nox": "nox", "ruff": "ruff check ."}[name]
                commands.setdefault("test" if name == "pytest" else "lint" if name == "ruff" else "check", command)
    if (workspace / "go.mod").is_file():
        commands.setdefault("test", "go test ./...")
    if (workspace / "Cargo.toml").is_file():
        commands.setdefault("test", "cargo test")
    if (workspace / "CMakeLists.txt").is_file() and re.search(r"(?im)^\s*enable_testing\s*\(", _read_limited(workspace / "CMakeLists.txt")):
        commands.setdefault("test", "ctest --test-dir <configured-build-directory> --output-on-failure")

    ci_workflows, ci_sources = _ci_profile(workspace)
    test_paths = sorted({path.relative_to(workspace).as_posix() for path in workspace.iterdir() if path.is_dir() and re.fullmatch(r"(?i)(tests?|__tests__)", path.name)})
    sources = [str(path.relative_to(workspace)) for path in [readme, *(workspace / name for name in manifests), *(workspace / name for name in style_files)] if path]
    sources.extend(ci_sources)
    if makefile:
        sources.append(makefile.relative_to(workspace).as_posix())
    if (workspace / "AGENTS.md").is_file():
        sources.append("AGENTS.md")
    profile: dict[str, Any] = {
        "workspace": str(workspace), "summary": summary, "manifests": manifests,
        "ecosystems": sorted({MANIFESTS[name] for name in manifests}),
        "languages": languages, "style_files": style_files,
        "top_level": top_level, "commands": commands, "test_paths": test_paths,
        "ci_workflows": ci_workflows,
        "sources": list(dict.fromkeys(sources)),
    }
    agents_path = workspace / "AGENTS.md"
    if agents_path.is_file():
        agents_bytes = agents_path.read_bytes()
        existing = agents_bytes.decode("utf-8", errors="replace")
        profile["agents"] = assess_agents(existing, profile, hashlib.sha256(agents_bytes).hexdigest())
    else:
        profile["agents"] = assess_agents(None, profile)
    return profile


def readiness_report(profile: dict[str, Any]) -> str:
    agents = profile["agents"]
    commands = "\n".join(f"- `{name}`: `{command}` (detected from configuration; not run by init)" for name, command in profile["commands"].items()) or "- No build or test command was established from repository configuration."
    workflows = "\n".join(
        f"- `{item['path']}`" + (f" (jobs: {', '.join(item['jobs'])})" if item["jobs"] else "")
        for item in profile["ci_workflows"]
    ) or "- No recognized CI configuration detected."
    tests = ", ".join(f"`{path}`" for path in profile["test_paths"]) or "no conventional top-level test directory detected"
    findings = "\n".join(f"- {item}" for item in agents["findings"]) or "- No instruction-file gaps detected by the current checks."
    sources = ", ".join(f"`{item}`" for item in profile["sources"]) or "none"
    return f"""# Project readiness

- Repository: `{profile['workspace']}`
- AGENTS.md status: **{agents['status']}**
- Evidence sources: {sources}

## Build and test conventions

{commands}

Test locations: {tests}.

## CI conventions

{workflows}

CI commands are read from configuration and are not executed by `init`.

## Instruction-file findings

{findings}

This report is heuristic and evidence-based. Review the cited repository files before relying on inferred commands. A draft is available when AGENTS.md is missing or has findings; adopting it requires an explicit review decision.
"""


def agents_draft(profile: dict[str, Any], existing_agents: str | None = None) -> str:
    commands = "\n".join(f"- {name}: `{command}` (detected from configuration; not run by init)" for name, command in profile["commands"].items()) or "- No command was established from repository configuration. Inspect project configuration and CI before running or inventing commands."
    tests = ", ".join(f"`{path}`" for path in profile["test_paths"]) or "not established; inspect project configuration before adding tests"
    workflows = "\n".join(f"- `{entry['path']}`: {', '.join(entry['commands']) or 'inspect its job steps for required checks'}" for entry in profile["ci_workflows"]) or "- No GitHub Actions workflow detected; check for another CI provider before assuming there is no CI."
    sources = ", ".join(f"`{item}`" for item in profile["sources"]) or "none"
    if existing_agents is not None:
        base = existing_agents.rstrip()
        separator = "\n\n" if base else ""
        return f"""{base}{separator}## Evidence-backed repository setup (0xSDLC draft)

> Proposed addition generated from current repository evidence. Existing instructions above are preserved. Review commands and checks before adoption. Sources: {sources}.

### Build and verification commands

{commands}

### Test locations

{tests}

### CI checks

{workflows}

These checks are read from configuration and were not executed by `init`.

### Repository conventions

- Follow the repository configuration in: {', '.join(f'`{path}`' for path in profile['style_files']) or 'no recognized formatter or contribution files detected'}.
- Inspect the relevant package/build manifest and CI workflow before selecting checks for a change.
- Run the narrowest relevant checks and report exact commands, results, and limitations.
"""

    structure = "\n".join(f"- `{name}`" for name in profile["top_level"]) or "- No visible project entries found."
    languages = ", ".join(f"{name} ({count} files sampled)" for name, count in profile.get("languages", {}).items()) or "not established"
    return f"""# Project instructions

> Generated draft. Review every inferred statement before adopting it. Evidence sources: {sources}.

## Mission

{profile['summary']}

## Detected environment

- Ecosystems: {', '.join(profile['ecosystems']) or 'not established'}
- Manifests: {', '.join(profile['manifests']) or 'none detected'}
- Languages: {languages}
- Tooling evidence: {', '.join(profile['style_files']) or 'none detected'}

## Build and test commands

{commands}

## Test locations

{tests}

## CI checks

{workflows}

## Repository structure

{structure}

## Working rules

- Read the task specification and nearest applicable instructions before editing.
- Inspect existing conventions before introducing a new pattern.
- Keep changes scoped and preserve unrelated user work.
- Run the narrowest relevant checks and report exact evidence and limitations.
- Treat repository configuration and established local code as stronger evidence than generic language guidance.
- Do not introduce a design pattern without a concrete problem, alternatives, and a testable benefit.
- Do not perform broad style cleanup as part of an unrelated task.

## Approval boundaries

- Ask before dependencies, CI/release configuration, public APIs, data migrations, destructive operations, secrets, or external side effects.
- Never expose credentials, weaken security or tests, or claim checks that were not run.
"""
