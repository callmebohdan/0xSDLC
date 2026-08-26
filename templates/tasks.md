---
schema_version: "0.1"
task_id: "{{task_id}}"
phase: "decompose"
status: "ready"
agent: "task-planner"
inputs: ["spec.md", "plan.md", "audit.md"]
assumptions: []
---

# Implementation tasks

<!-- Keep each task independently understandable, implementable, and verifiable. -->

## Traceability

| Requirement/criterion | Task IDs | Final evidence |
| --- | --- | --- |
| FR-1 / AC-1 | | |

## Dependency order

```text
T1 → T2 → T3
```

Explain any parallel branches and how file conflicts are prevented.

## Task T1 — [short outcome]

- Intent / user value:
- Scope:
- Files likely touched:
- Depends on:
- Preconditions:
- Implementation notes:
- Acceptance checks:
- Evidence required:
- Rollback/recovery:
- Parallel-safe: `yes` / `no`; reason:
- Approval required: `yes` / `no`; reason:
- Done means:

## Task T2 — [short outcome]

- Intent / user value:
- Scope:
- Files likely touched:
- Depends on:
- Preconditions:
- Implementation notes:
- Acceptance checks:
- Evidence required:
- Rollback/recovery:
- Parallel-safe: `yes` / `no`; reason:
- Approval required: `yes` / `no`; reason:
- Done means:

## Integration and final verification

- Cross-task checks:
- User journey check:
- Regression check:
- Required human decision:
