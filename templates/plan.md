---
schema_version: "0.2"
task_id: "{{task_id}}"
phase: "plan"
status: "ready"
agent: "task-planner"
inputs: ["brief.md", "spec.md", "audit.md", "design.md"]
assumptions: []
---

# Implementation plan

<!-- A plan is a set of decisions and evidence paths. It is not implementation code. -->

## Requirements and invariants addressed

| Requirement/criterion | Planned mechanism | Evidence |
| --- | --- | --- |

## Chosen approach

- Summary:
- Why it fits the existing repository:
- New concepts introduced:
- Concepts intentionally not introduced:

## Alternatives considered

| Option | Benefit | Cost/risk | Decision |
| --- | --- | --- | --- |

## File-level changes

| Path | Action | Reason | Risk/approval |
| --- | --- | --- | --- |

## Data and control flow

1. Input/precondition:
2. Main flow:
3. Validation/authorization:
4. State/persistence:
5. Error/retry/rollback:
6. Output/observability:

## Compatibility and security

- Public contract impact:
- Data migration:
- Backward compatibility:
- Authentication/authorization:
- Input/output trust boundaries:
- Sensitive data handling:

## Test and evidence strategy

| Criterion | Test/check/inspection | Fixture or setup | Expected evidence |
| --- | --- | --- | --- |

## Execution order and approvals

1.

## Implementation slices

| ID | Outcome | Files/seams | Depends on | Acceptance check | Parallel-safe |
| --- | --- | --- | --- | --- | --- |
| T1 | | | | | yes/no |

Each slice must be independently understandable, implementable, and provable. Do not create a separate decomposition artifact for the normal route.

- Human approval required for:
- Safe stopping points:

## Rollback or recovery

- Reversible change:
- Data recovery:
- Feature flag/config rollback:
- Failure signal:

## Non-goals and residual risks

-
