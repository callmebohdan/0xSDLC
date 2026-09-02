# Local rollout

## Prerequisites

- Python 3.10 or newer. Python 3.14 is supported.
- A repository with a root `AGENTS.md` or an agreed project instruction file.
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

The default destination is `%USERPROFILE%\\.agents\\0xsdlc` on Windows and `~/.agents/0xsdlc` on macOS/Linux. The installer refuses to publish into a non-empty destination unless `--force` is supplied.

For a controlled location:

```text
python scripts\install.py --agents-dir C:\path\to\.agents\0xsdlc
```

Set `0XSDLC_AGENTS_HOME` to make the orchestrator use another published copy. The repository's root-level contract folders remain the source fallback.

## Dry-run first

```text
python scripts\0xsdlc.py autopilot "Add CSV export to reports"
python scripts\0xsdlc.py status
```

Inspect `%USERPROFILE%\\.agents\\0xsdlc\\sessions\\<task-id>\\brief.md`, `route.json`, and the first prompt before execution. For a high-risk task, record approval with `python scripts\\0xsdlc.py approve <task-id> --by "Name" --scope "Exact approved scope"`, then continue with `resume`.

The single rollout command publishes the runtime contracts and registers portable skills for supported local AI tools:

```text
python scripts\\install.py --force
```

On Windows, this installs contracts into `%USERPROFILE%\\.agents\\0xsdlc` and skills into `%USERPROFILE%\\.codex\\skills`, `%USERPROFILE%\\.claude\\skills`, `%USERPROFILE%\\.cursor\\skills`, and `%USERPROFILE%\\.agents\\skills`. Use `--agents-dir`, `--codex-skills-dir`, `--claude-skills-dir`, `--cursor-skills-dir`, or `--portable-skills-dir` only when you intentionally use custom locations. Use `--skip-provider-skills` for a contracts-only rollout; the old `--skip-codex-skills` name remains as a compatibility alias.

## Configure a provider

```powershell
$env:0XSDLC_CODEX_COMMAND = 'codex exec --file {prompt_file}'
python scripts\0xsdlc.py autopilot "Add CSV export to reports" --model codex --execute
```

Start with a harmless test task. Review the provider's tool permissions and command semantics before giving it write access.

## Validation

```text
python scripts\validate_harness.py
```

Validation checks the repository source library and manifest. It does not prove that a provider CLI is installed, that a remote model is available, or that an application task is correct.

## Updating the library

1. Change the versioned files under the root-level `0xSDLC-*`, `support/adapters/`, `templates/`, or convention folders.
2. Run validation and a representative dry-run.
3. Review the diff as a harness change.
4. Republish with `scripts/install.py`.
5. Record compatibility or migration notes if contracts or templates changed.
