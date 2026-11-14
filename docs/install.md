# Local rollout

## Prerequisites

- Python 3.10 or newer. Python 3.14 is supported.
- A repository to inspect. `init` checks whether root `AGENTS.md` is missing or lacks guidance reflected in repository build, test, CI, and style evidence; it prepares a task-local draft for review before adoption.
- An installed provider CLI only if `--execute` will be used.

On Windows, use a fresh terminal after changing PATH. If PATH is not refreshed, call the interpreter directly, for example:

```powershell
& 'C:\Users\bohan\AppData\Local\Programs\Python\Python314\python.exe' scripts\validate_harness.py
```

## Publish the global contract library

From this repository:

```text
python scripts\install.py
```

The shared runtime library is installed into `%USERPROFILE%\\.agents\\0xsdlc` on Windows or `~/.agents/0xsdlc` on macOS/Linux. Project instructions and project task artifacts use the current repository: `AGENTS.md` (plus applicable nested `AGENTS.md` files) and `<project-root>/.agents/0xSDLC/sessions/<task-id>/`. These locations serve different purposes.

The first install refuses occupied destinations unless you request an upgrade. `--upgrade` (the backward-compatible `--force` alias) replaces only the published 0xSDLC contract paths and the three named 0xSDLC skill folders. It preserves legacy runtime `sessions/`, project-local `.agents/0xSDLC/sessions/`, sibling skills, and other files outside those managed paths. Edits inside a published contract or 0xSDLC skill folder are replaced by the repository copy. The installer checks every destination before writing and stages updates so a provider-skill collision cannot leave only the runtime updated.

For a controlled location:

```text
python scripts\install.py --agents-dir C:\path\to\.agents\0xsdlc
```

Set `0XSDLC_AGENTS_HOME` to make the orchestrator use another published copy. The repository's root-level contract folders remain the source fallback.

## Dry-run first

Initialize a repository and inspect its build, test, CI, and `AGENTS.md` readiness before the first task:

```text
python scripts\0xSDLC.py init --workspace C:\path\to\repo
```

Use `--check` for a console-only report. If the instructions need work, review the session's `readiness.md` and `agents-draft.md`, then adopt the reviewed draft with the printed `init --adopt ... --approve ...` command.

```text
python scripts\0xSDLC.py autopilot "Add CSV export to reports"
python scripts\0xSDLC.py status
```

Inspect `<project-root>\\.agents\\0xSDLC\\sessions\\<task-id>\\brief.md`, `route.json`, and the first prompt before execution. The runtime library path is not used for new project sessions.

The single rollout command publishes runtime contracts plus portable Codex, Claude Code, Cursor, and shared skill wrappers:

```text
python scripts\\install.py --upgrade
```

The default skill destinations are the user-level `.codex/skills`, `.claude/skills`, `.cursor/skills`, and `.agents/skills` directories. Provider-specific directory options support custom locations, and `--skills-dir` remains a backward-compatible alias for the Codex destination. Use `--skip-provider-skills` for a contracts-only rollout. You can repeat an initial install with no flags only when all targets are empty; use `--upgrade` to replace the managed 0xSDLC paths in an existing installation.

Filesystem placement does not prove interactive discovery. Restart or rescan each host and run a harmless invocation before recording live conformance.

## Configure a provider

```powershell
$env:0XSDLC_CODEX_COMMAND = 'codex exec --file {prompt_file}'
python scripts\0xSDLC.py autopilot "Add CSV export to reports" --model codex --execute
```

Start with a harmless test task. Review the provider's tool permissions and command semantics before giving it write access.

Engineering-practice supplements are published with the runtime contracts. They are selected automatically by phase and detected language. `--maintainability-review` also requires a provider profile with parallel-process capability because it runs beside the primary review.

## Validation

```text
python scripts\validate_harness.py
```

Validation checks the repository source library and manifest. It does not prove that a provider CLI is installed, that a remote model is available, or that an application task is correct.

## Updating the library

1. Change the versioned files under the root-level `0xSDLC-*`, `support/`, `templates/`, or convention folders.
2. Run validation and a representative dry-run.
3. Review the diff as a harness change.
4. Republish with `scripts/install.py --upgrade` to replace the managed 0xSDLC paths.
5. Record compatibility or migration notes if contracts or templates changed.
