---
schema_version: "0.2"
task_id: "{{task_id}}"
phase: "quality"
status: "ready"
agent: "quality-control"
inputs: ["brief.md", "spec.md", "implementation.md", "test-report.md", "review.md"]
assumptions: []
---

# Quality control and assurance report

## Artifact integrity

| Check | Evidence | Result |
| --- | --- | --- |
| Task IDs consistent | | |
| Required artifacts present | | |
| Statuses consistent | | |
| No secret/private data exposed | | |

## Traceability

| Requirement/criterion | Plan/task | Implementation | Test | Review | Result |
| --- | --- | --- | --- | --- | --- |

## Gate review

| Gate | Required? | Evidence/approval | Result |
| --- | --- | --- | --- |
| Functional tests | | | |
| Regression tests | | | |
| Security/privacy | | | |
| Compatibility/migration | | | |
| Human approval | | | |

## Findings and missing evidence

| ID | Severity | Gap/finding | Required action | Owner |
| --- | --- | --- | --- | --- |

## Decision

- Status: `ready` / `needs-review` / `blocked`
- Reason:
- Next phase:
