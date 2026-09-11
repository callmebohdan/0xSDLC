# Cursor adapter

Use this file as the Cursor-specific translation layer when Cursor is the execution surface. The root-level `0xSDLC-*` contracts, `support/conventions/`, and templates remain authoritative.

## Invocation model

Cursor may be used interactively, through a CLI wrapper, or through an automation bridge. Because the exact invocation and permission model can vary, record the actual execution surface in the task artifact:

- Cursor version or integration:
- Workspace opened:
- Prompt packet supplied:
- Tools/write permissions enabled:
- Human supervision present:

Do not pretend that an interactive Cursor session is equivalent to a deterministic CLI run unless the prompt, changes, and evidence are captured.

## Session rules

- Load only the active phase contract, listed artifacts, and relevant source.
- Start a fresh context at phase boundaries when practical.
- Inspect the working tree before editing.
- Use read-only mode for intake, specification, audit, design, planning, review, and verification.
- For implementation/fix work, limit edits to the assigned task and preserve unrelated user changes.
- Require the named artifact, exact checks, status, assumptions, risks, and next action.

## Guardrails

- Do not rely on Cursor autocomplete or chat history as durable evidence.
- Do not accept a visual preview as proof of backend, security, persistence, or accessibility behavior.
- Do not enable broad workspace or terminal permissions without reviewing the command and blast radius.
- Do not commit secrets, run destructive commands, or modify production systems through an unsupervised session.

## Handoff

Export or record the resulting diff, commands, test output, and phase artifact under `.agents/0xsdlc/sessions/<task-id>/`. If the interactive session cannot provide reproducible evidence, mark the phase `needs-review` rather than `verified`.
