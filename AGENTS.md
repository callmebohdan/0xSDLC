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

## Engineering standards

- Keep the runner compatible with Python 3.10+ and dependency-free unless a dependency is explicitly approved.
- Separate orchestration state, routing policy, provider translation, prompt assembly, storage, and project discovery rather than growing a monolithic entry point.
- Prefer typed, focused functions and explicit persisted state over hidden globals or provider-specific behavior.
- Preserve route/artifact backward compatibility or add an explicit migration with regression coverage.
- Keep Markdown contracts self-contained but load them selectively; new guidance must justify its prompt and model-call cost.
- Use design patterns only for a demonstrated current need. Record the simpler alternative, added indirection, and test seam.
- Extend deterministic fake-adapter tests for routing, recovery, artifact, cost/call-count, and installation behavior before claiming harness support.

## Output style

Use concise Markdown. Prefer tables and checklists over prose. Every claim about correctness must point to evidence: a command, file, test, or explicit human decision.
