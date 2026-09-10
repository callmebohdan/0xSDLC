---
name: "0xsdlc-autopilot"
description: "Run or prepare a bounded 0xSDLC spec-driven engineering cycle in the current repository."
disable-model-invocation: true
---

# 0xSDLC autopilot

Use the canonical contract in the user-level `.agents/0xsdlc/0xSDLC-autopilot/autopilot.md`. Treat the current task specification and repository `AGENTS.md` as authoritative. If `AGENTS.md` is absent, use task-local project context and suggest `$0xsdlc-bootstrap` or `/0xsdlc-bootstrap`; do not create permanent instructions silently.

Keep durable evidence under `.agents/0xsdlc/sessions/YYYY-MM-DD_short-description_8hex/` in the user-level runtime. Choose the smallest safe route, preserve evidence, stop at human gates, and never invoke another provider CLI unless explicitly requested.
