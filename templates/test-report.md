---
schema_version: "0.2"
task_id: "{{task_id}}"
phase: "test"
status: "ready"
test_outcome: "pass"
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

Use `pass`, `fail`, `blocked`, `needs-review`, or `not-required`. If a required check cannot run because a command, permission, service, or tool is unavailable, do not mark the affected criterion as passing.

## Edge and negative cases

| Case | Expected | Actual | Evidence | Result |
| --- | --- | --- | --- | --- |

## Failures and classification

| Failure | Classification | Exact command / working directory / exit code | Exact error excerpt or stderr artifact path | Impact | Owner/next action |
| --- | --- | --- | --- | --- | --- |

Preserve the original command and concise error output (or a path to the complete stderr artifact) before trying a workaround. Classify platform, dependency, network, service, and permission failures as `environment`; record the workaround and rerun as separate evidence. Redact secrets and personal data, not diagnostic details needed to reproduce the failure.

## Coverage gaps and limitations

- Untested behavior:
- Unavailable service/tool:
- Flaky or skipped test:
- Environment limitation:

## Recommendation

- Status: `ready` / `needs-review` / `blocked`
- Test outcome: `pass` / `fail` / `needs-review`
- Stable `blocking_findings` IDs when outcome is `fail` (required for bounded automatic repair)
- Reason:
- Next action:
