---
name: "0xsdlc-bootstrap"
description: "Assess repository readiness and prepare evidence-based AGENTS.md guidance when instructions are missing or inadequate."
disable-model-invocation: true
---

# 0xSDLC project bootstrap

Use `.agents/0xsdlc/support/agents/0xSDLC-bootstrap/bootstrap.md` as the canonical contract. Start with `scripts/0xSDLC.py init --check --workspace <repo>` for a quick report, or run `init` to save a report and an evidence-based draft when root `AGENTS.md` is missing or has detected gaps. Do not create or update repository instructions without explicit human approval. Existing instructions are preserved in the proposed update, and adoption verifies that they have not changed since the draft was prepared.

Use `scripts/0xSDLC.py init --workspace <repo>` from the installed runtime to prepare the report and draft. `bootstrap` remains a compatible alias. Session storage uses `--sessions-root`, then `0XSDLC_SESSIONS_ROOT`, then `<project-root>/.agents/0xSDLC/sessions`. If the default is denied and no root was requested, pass a writable Git-ignored directory. After approval, adopt the reviewed draft by its full session path.
