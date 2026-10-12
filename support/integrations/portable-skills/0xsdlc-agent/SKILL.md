---
name: "0xsdlc-agent"
description: "Run one named 0xSDLC phase agent such as specify, audit, design, plan, implement, test, review, quality-control, fix, or verify in the current repository."
disable-model-invocation: true
---

# 0xSDLC phase agent

Use the named phase contract under the user-level `.agents/0xsdlc` directory (Windows: `%USERPROFILE%\\.agents\\0xsdlc`). Supported phase names are `specify`, `audit`, `design`, `plan`, `implement`, `test`, `review`, `quality-control`, `fix`, and `verify`; select the corresponding contract under `support/agents/` or the root-level `0xSDLC-*` folders. Read only the selected contract, the current repository `AGENTS.md`, the task brief, and relevant prior artifacts. `quality-control` is a manual/opt-in evidence-integrity gate and is never added to the default route.

Keep durable evidence under the user-level `.agents/0xsdlc/sessions/YYYY-MM-DD_short-description_XXXXXXXX/` directory. Perform only the requested phase, preserve the specification as source of truth, run the narrowest relevant checks, and report changed files, commands, evidence, assumptions, failures, and remaining risks. Ask before dependencies, CI/release changes, public API changes, migrations, destructive actions, or secrets. This portable skill may be exposed by a host as `$0xsdlc-agent`, `/0xsdlc-agent`, or another provider-native action; the host syntax does not change the contract.
