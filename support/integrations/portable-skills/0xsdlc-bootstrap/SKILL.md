---
name: "0xsdlc-bootstrap"
description: "Draft evidence-based AGENTS.md project instructions for a repository that does not have them."
disable-model-invocation: true
---

# 0xSDLC project bootstrap

Use `.agents/0xsdlc/support/agents/0xSDLC-bootstrap/bootstrap.md` as the canonical contract. Inspect the current repository and create a reviewable task-local draft. Do not overwrite or silently create repository instructions; ask for human approval before adopting the draft as root `AGENTS.md`.

Use `scripts/0xSDLC.py bootstrap --workspace <repo>` from the installed runtime to prepare the draft. Session storage uses `--sessions-root`, then `0XSDLC_SESSIONS_ROOT`, then `<project-root>/.agents/0xsdlc/sessions`. If the default is denied and no root was requested, pass a writable Git-ignored directory. After approval, adopt the reviewed draft by its full session path.
