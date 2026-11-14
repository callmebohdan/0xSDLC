---
name: "0xsdlc-autopilot"
description: "Run or prepare a bounded 0xSDLC spec-driven engineering cycle in the current repository."
disable-model-invocation: true
---

# 0xSDLC autopilot

Use the installed canonical contract from `0XSDLC_AGENTS_HOME` when set, otherwise the user-level `.agents/0xsdlc` directory (Windows: `%USERPROFILE%\\.agents\\0xsdlc`). Read `0xSDLC-autopilot/autopilot.md` and the relevant phase contracts under that library. Resolve the project root from the current workspace (Git root when available). Read its root `AGENTS.md` and the nearest nested `AGENTS.md` files that apply to the files being inspected or changed; do not treat the installed runtime's own `AGENTS.md` as project policy. The user's task specification and applicable project instructions govern the work. If root instructions are missing or inadequate, use the task-local readiness context and point to `init --check` or `$0xsdlc-bootstrap`/`/0xsdlc-bootstrap`; do not create or update permanent rules silently.

Use the installed `scripts/0xSDLC.py` from that runtime directory. Prepare with `autopilot "<request>" --native`. Use the task's `--sessions-root` when supplied, then `0XSDLC_SESSIONS_ROOT`, then `<project-root>/.agents/0xSDLC/sessions`. Do not store new project sessions under the shared runtime library. If the default is denied and no root was requested, choose a writable Git-ignored directory and pass it with `--sessions-root`. Read `docs/session-output.md` in the runtime for recorder commands.

For chat use, prepare the route and explain the next phase. When asked to execute, use `native open` before working on each phase, write the report to the returned artifact path, and use `native close` with its outcome. Use `native interrupt` to recover an abandoned attempt. Follow approval boundaries and preserve earlier attempts. Launch external model CLIs only when the user explicitly requests adapter execution.
