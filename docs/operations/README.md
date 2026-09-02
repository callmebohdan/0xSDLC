# Run instructions

This folder explains how to load and execute the root-level 0xSDLC subagents.

## Loading order

1. Root `AGENTS.md`.
2. `support/conventions/phase-protocol.md`.
3. `support/conventions/boundaries.md`.
4. `support/conventions/output-contract.md`.
5. The active phase's domain-named contract, such as `planning.md` or `verification.md`.
6. The active artifact template in `templates/`.
7. Only the listed task artifacts and relevant source files.

Before loading additional context, consult `support/conventions/context-budget.md`. Use the minimal tier by default; extended context requires a concrete risk or cross-system reason.

Do not load every phase into every prompt. The active phase owns the current action; later phases should not be simulated early.

## Starting autopilot

```powershell
python scripts\0xsdlc.py autopilot "Describe one bounded task"
```

Inspect the generated route and first prompt under `%USERPROFILE%\\.agents\\0xsdlc\\sessions\\<task-id>\\`. Use `--execute` only after the adapter and permissions are understood.

Use `--parallel-checks` only with `--full` when independent audit and review lanes add meaningful confidence. It doubles those model calls and is disabled by default.

## Phase handoff

Every phase writes its required artifact, status, evidence, assumptions, risks, and next action. If a phase cannot proceed safely, write `blocked` or `needs-review` rather than improvising.
