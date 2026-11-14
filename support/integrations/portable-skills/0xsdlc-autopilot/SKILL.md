---
name: "0xsdlc-autopilot"
description: "Run or prepare a bounded 0xSDLC spec-driven engineering cycle in the current repository."
disable-model-invocation: true
---

# 0xSDLC autopilot

Use the installed canonical contract at the user-level `.agents/0xsdlc/0xSDLC-autopilot/autopilot.md` (Windows: `%USERPROFILE%\\.agents\\0xsdlc\\0xSDLC-autopilot\\autopilot.md`) and the relevant phase contracts under the same directory. Treat the user's task specification and the current repository's `AGENTS.md` as authoritative. If `AGENTS.md` is absent, use task-local project context and suggest `$0xsdlc-bootstrap` or `/0xsdlc-bootstrap`; do not create permanent instructions silently.

Use the installed `scripts/0xSDLC.py` from the same runtime directory. Prepare with `autopilot "<request>" --native`. Use the task's `--sessions-root` when supplied, then `0XSDLC_SESSIONS_ROOT`, then the existing default. If the default is denied and no root was requested, choose a writable Git-ignored directory and pass it with `--sessions-root`. Read `docs/session-output.md` in the runtime for recorder commands.

For chat use, prepare the route and explain the next phase. When asked to execute, use `native open` before working on each phase, write the report to the returned artifact path, and use `native close` with its outcome. Use `native interrupt` to recover an abandoned attempt. Follow approval boundaries and preserve earlier attempts. Launch external model CLIs only when the user explicitly requests adapter execution.
