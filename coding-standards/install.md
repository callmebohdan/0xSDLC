# Local install standard

## Requirements

- Python 3.10 or newer; Python 3.14 is supported.
- A fresh terminal after changing PATH on Windows.
- A provider CLI only when using `--execute`.

## Publish the instruction library

```powershell
python Scripts\install.py
```

This publishes the root-level contracts to `%USERPROFILE%\.agents\0xsdlc` on Windows or `~/.agents/0xsdlc` elsewhere. Use `--agents-dir` for an explicit location and `--force` only after reviewing an existing destination.

## Validate

```powershell
python Scripts\validate_harness.py
```

## Run a supervised dry-run

```powershell
python scripts\0xSDLC.py autopilot "Describe one bounded task"
python scripts\0xSDLC.py status
```

Inspect `.agents/0xsdlc/sessions/<task-id>/` before enabling adapter execution.
