# Local install standard

## Requirements

- Python 3.10 or newer; Python 3.14 is supported.
- A fresh terminal after changing PATH on Windows.
- A provider CLI only when using `--execute`.

## Publish the instruction library

```powershell
python Scripts\install.py
```

This publishes the shared contracts to `%USERPROFILE%\.agents\0xsdlc` on Windows or `~/.agents/0xsdlc` elsewhere. Use `--agents-dir` for an explicit location. For an existing install, use `--upgrade` (`--force` is a compatible alias); it replaces only published contract paths and named 0xSDLC skill folders, and preserves project sessions, legacy runtime sessions, unrelated files outside managed paths, and sibling skills. The installer preflights all targets before making changes.

## Validate

```powershell
python Scripts\validate_harness.py
```

## Run a supervised dry-run

```powershell
python scripts\0xSDLC.py autopilot "Describe one bounded task"
python scripts\0xSDLC.py status
```

Inspect `<project-root>/.agents/0xSDLC/sessions/<task-id>/` before enabling adapter execution. Read the project root `AGENTS.md` and the nearest nested instruction files applicable to the task; the installed runtime's own `AGENTS.md` is shared 0xSDLC policy, not project policy.
