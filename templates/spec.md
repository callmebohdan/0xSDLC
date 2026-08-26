---
schema_version: "0.1"
task_id: "{{task_id}}"
phase: "specify"
status: "ready"
agent: "specifier"
inputs: ["brief.md"]
assumptions: []
---

# Specification

<!-- Write behavior and evidence, not a premature implementation plan. Give every important requirement an ID. -->

## Problem, users, and outcome

- Problem:
- Primary users/actors:
- Desired outcome:
- Why this matters:

## User journeys

### J1 — Primary journey

1. Given:
2. When:
3. Then:

### J2 — Failure, empty, or recovery journey

1. Given:
2. When:
3. Then:

## Functional requirements

| ID | Requirement | Priority | Observable evidence |
| --- | --- | --- | --- |
| FR-1 | | Must/Should | |

## Non-functional requirements

| ID | Area | Requirement / threshold | Evidence |
| --- | --- | --- | --- |
| NFR-1 | Security/performance/accessibility/reliability/compatibility/operations | | |

## Acceptance criteria

<!-- Each criterion must be independently testable. Avoid “works well” or “secure” without observable detail. -->

| ID | Given | When | Then | Evidence type |
| --- | --- | --- | --- | --- |
| AC-1 | | | | |

## Edge cases and failure behavior

- Empty or missing input:
- Invalid or malformed input:
- Boundary values / large input:
- Duplicate request / retry / idempotency:
- Unauthorized or forbidden actor:
- Concurrent or partial failure:
- Network/service unavailable:
- Time, locale, timezone, encoding:
- Backward compatibility:

## Invariants

-

## Boundaries and non-goals

-

## Decisions and unresolved questions

| ID | Decision/question | Options | Decision owner | Status |
| --- | --- | --- | --- | --- |

## Definition of done

- [ ] Every Must requirement has acceptance evidence.
- [ ] Failure behavior is specified.
- [ ] Security, privacy, and compatibility impact is addressed.
- [ ] Tests or other evidence can be run without guessing.
- [ ] Human approvals are identified.
