---
schema_version: "0.1"
task_id: "{{task_id}}"
phase: "test"
status: "ready"
agent: "tester"
inputs: ["spec.md", "implementation.md", "audit.md"]
assumptions: []
---

# Test report

## Test scope

- Implementation/task slice:
- Acceptance criteria under test:
- Excluded checks and why:
- Environment/platform:

## Baseline

- Baseline command:
- Baseline result:
- Pre-existing failures:

## Commands run

| Command | Working directory | Exit code | Result | Duration/limit |
| --- | --- | ---: | --- | --- |

## Acceptance criteria results

| Criterion | Scenario/input | Expected | Actual | Evidence | Result |
| --- | --- | --- | --- | --- | --- |

## Edge and negative cases

| Case | Expected | Actual | Evidence | Result |
| --- | --- | --- | --- | --- |

## Failures and classification

| Failure | Classification | Reproduction | Impact | Owner/next action |
| --- | --- | --- | --- | --- |

## Coverage gaps and limitations

- Untested behavior:
- Unavailable service/tool:
- Flaky or skipped test:
- Environment limitation:

## Recommendation

- Status: `ready` / `needs-review` / `blocked`
- Reason:
- Next action:
