---
name: "0xsdlc-autopilot"
description: "Run or prepare a bounded 0xSDLC spec-driven engineering cycle in the current repository."
disable-model-invocation: true
---

# 0xSDLC autopilot

Use the installed canonical contract at the user-level `.agents/0xsdlc/0xSDLC-autopilot/autopilot.md` (Windows: `%USERPROFILE%\\.agents\\0xsdlc\\0xSDLC-autopilot\\autopilot.md`) and the relevant phase contracts under the same directory. Treat the user's task specification and the current repository's `AGENTS.md` as authoritative. If `AGENTS.md` is absent, use task-local project context and suggest `$0xsdlc-bootstrap` or `/0xsdlc-bootstrap`; do not create permanent instructions silently.

Create or update durable evidence only under the user-level `.agents/0xsdlc/sessions/YYYY-MM-DD_short-description_XXXXXXXX/` directory. Keep the current repository's source tree focused on the requested change. Choose the smallest safe route, preserve evidence, stop at approval gates or missing proof, and never claim verification without commands or other concrete evidence.

For chat use, prepare the route and explain the next phase. When the user explicitly asks to execute, perform the routed phases in the current workspace and follow all approval and safety boundaries. Do not invoke external model CLIs from this skill unless the user explicitly requests that adapter execution. This portable skill may be exposed by a host as `$0xsdlc-autopilot`, `/0xsdlc-autopilot`, or another provider-native action; the host syntax does not change the contract.
