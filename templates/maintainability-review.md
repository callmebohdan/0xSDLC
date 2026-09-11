---
schema_version: "0.2"
task_id: "{{task_id}}"
phase: "review"
status: "ready"
decision: "approve" # approve | fix | needs-review
blocking_findings: []
agent: "maintainability-reviewer"
inputs: ["spec.md", "design.md", "implementation.md", "test-report.md"]
assumptions: []
---

# Maintainability review

## Scope and evidence

- Changed responsibilities:
- Dependency/interface boundaries inspected:
- Project rules and tool configuration:
- Applicable language profile:
- Areas not reviewed:

## Findings

| ID | Severity | Finding | Evidence | Change/scale impact | Smallest recommendation |
| --- | --- | --- | --- | --- | --- |

## Architecture fitness

- Cohesion and ownership:
- Coupling and dependency direction:
- State, errors, concurrency, and lifecycle:
- Testability and observability:
- Relevant scalability dimensions:

## Pattern and abstraction assessment

| Abstraction/pattern | Concrete need | Simpler alternative | Added cost | Verdict |
| --- | --- | --- | --- | --- |

## Recommendation

- Decision: `approve` / `fix` / `needs-review`
- Blocking finding IDs:
- Non-blocking follow-ups:
- Reason:
