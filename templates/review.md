---
schema_version: "0.2"
task_id: "{{task_id}}"
phase: "review"
status: "ready"
decision: "approve" # approve | fix | needs-review
blocking_findings: [] # stable finding IDs required when decision is fix
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

When `decision: fix`, put every finding that must be fixed in `blocking_findings` using the IDs in this table (for example, `["F-001", "F-004"]`). Preserve an ID across a re-review when the same issue remains open. A missing or unstable ID stops automatic retries and asks for human review; this prevents an unbounded loop that merely renames the same defect.

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
- Cohesion/dependency direction:
- Ownership/lifetime/concurrency:
- Pattern or abstraction justification:
- Language-specific tool evidence:

## Recommendation

- Decision: `approve` / `fix` / `needs-review`
- Blocking finding IDs:
- Reason:
