# 0xSDLC project instructions

## Mission

Maintain 0xSDLC as a lightweight, model-neutral, spec-driven coding harness. Optimize for reliable artifacts and cheap context, not maximum agent count.

## Required behavior

- Read the task brief and the relevant root-level `0xSDLC-*` contract before acting. If a system-level copy exists, the orchestrator may use it as the runtime contract source.
- Treat the current task spec as the source of truth. If implementation and spec disagree, record the discrepancy; do not silently rewrite requirements.
- Work in small, testable slices. Keep unrelated cleanup out of the task.
- Prefer existing project commands and conventions. Discover them before inventing new tooling.
- Produce the phase output contract even when the phase is blocked.
- Report assumptions, changed files, commands run, failures, and remaining risks.

## Boundaries

- Always: preserve user changes, run the narrowest relevant checks, and leave an evidence trail.
- Ask first: adding dependencies, changing CI/release configuration, changing a public API, migrations, or deleting/renaming user files.
- Never: expose secrets, bypass failing tests, weaken security controls, or claim verification that was not run.

## Source layout

- `0xSDLC-*`: root-level model-facing phase/subagent contracts.
- Root `0xSDLC-*` folders: autopilot and frequently invoked phase contracts.
- `support/`: provider contracts, less-frequent phase agents, adapters, MCP boundaries, and shared rules.
- `scripts/`: small, dependency-free Python utilities.
- `.agents/0xsdlc/sessions/`: generated local artifacts; do not treat them as source code.

## Output style

Use concise Markdown. Prefer tables and checklists over prose. Every claim about correctness must point to evidence: a command, file, test, or explicit human decision.
