---
name: "0xsdlc-agent"
description: "Run one named 0xSDLC phase agent such as specify, audit, design, plan, implement, test, review, quality-control, fix, or verify in the current repository."
disable-model-invocation: true
---

# 0xSDLC phase agent

Use the named phase contract under the user-level `.agents/0xsdlc` directory (Windows: `%USERPROFILE%\\.agents\\0xsdlc`). Supported phase names are `specify`, `audit`, `design`, `plan`, `implement`, `test`, `review`, `quality-control`, `fix`, and `verify`; select the corresponding contract under `support/agents/` or the root-level `0xSDLC-*` folders. Read only the selected contract, the current repository `AGENTS.md`, the task brief, and relevant prior artifacts. `quality-control` is a manual/opt-in evidence-integrity gate and is never added to the default route.

Use the installed `scripts/0xSDLC.py` and its `docs/session-output.md`. In an existing native task, open the requested routed phase with `native open`. For standalone work, first prepare `autopilot "<request>" --native --phase <phase>`. Use `--sessions-root` when supplied, then `0XSDLC_SESSIONS_ROOT`, then `<project-root>/.agents/0xSDLC/sessions`. If the default is denied and no root was requested, pass a writable Git-ignored directory.

Perform only the requested phase. Write its report to the path returned by `native open`, then use `native close` with the outcome. Use `native interrupt` to recover an abandoned attempt. Preserve the specification as source of truth and report changed files, commands, evidence, assumptions, failures, and remaining risks. Ask before dependencies, CI/release changes, public API changes, migrations, destructive actions, or secrets.
