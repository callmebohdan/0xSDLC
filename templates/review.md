---
schema_version: "0.1"
task_id: "{{task_id}}"
phase: "review"
status: "ready"
decision: "approve" # approve | fix | needs-review
agent: "reviewer"
inputs: ["brief.md", "spec.md", "plan.md", "implementation.md", "test-report.md"]
assumptions: []
---

# Review report

## Review scope

- Diff/commit reviewed:
- Files inspected:
- Artifacts inspected:
- Areas not reviewed:

## Findings

| ID | Severity | Finding | Evidence | Impact | Recommendation |
| --- | --- | --- | --- | --- | --- |

Use `P0` for immediate security/data-loss/system blockers, `P1` for serious correctness or contract defects, `P2` for meaningful defects or weak evidence, and `P3` for minor follow-ups.

## Spec conformance

| Criterion | Implementation evidence | Test evidence | Finding |
| --- | --- | --- | --- |

## Security and trust boundaries

- Input validation:
- Authentication/authorization:
- Secrets/privacy:
- Injection/data exposure:
- Logging/observability:
- Dependency/supply-chain impact:

## Maintainability and operations

- Existing patterns preserved:
- Error/retry behavior:
- Compatibility/migration:
- Performance/resource use:
- Accessibility/user experience:
- Rollback/recovery:

## Recommendation

- Decision: `approve` / `fix` / `needs-review`
- Blocking finding IDs:
- Reason:
