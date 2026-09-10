---
schema_version: "0.2"
task_id: "{{task_id}}"
phase: "verify"
status: "needs-review"
agent: "verifier"
inputs: ["brief.md", "spec.md", "implementation.md", "test-report.md", "review.md"]
assumptions: []
---

# Verification

<!-- `verified` is a proof decision, not a confidence statement. Every required criterion needs evidence. -->

## Verification scope

- Current route and phase:
- Implementation version/diff:
- Spec version:
- Reviewer/test report versions:

## Acceptance-criteria evidence

| Criterion | Direct evidence | Evidence freshness | Result | Gap/action |
| --- | --- | --- | --- | --- |

## Required gates

| Gate | Required? | Evidence/approval | Result |
| --- | --- | --- | --- |
| Tests | | | |
| Review | | | |
| Security/privacy | | | |
| Migration/public contract | | | |
| Human approval | | | |

## Unresolved failures, gaps, and risks

-

## Decision

- Status: `verified` / `needs-review` / `blocked`
- Decision rationale:
- Accepted by / timestamp, if applicable:

## Handoff

- Changed files:
- Commands/evidence to reproduce:
- Residual risks:
- Next action:
