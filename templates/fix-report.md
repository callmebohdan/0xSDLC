---
schema_version: "0.1"
task_id: "{{task_id}}"
phase: "fix"
status: "ready"
agent: "fixer"
inputs: ["spec.md", "plan.md", "test-report.md", "review.md", "verification.md"]
assumptions: []
---

# Fix report

## Finding addressed

- Finding ID:
- Source artifact:
- Original statement:
- Expected behavior:

## Reproduction

- Command/scenario:
- Before result:
- Evidence:

## Root cause

- Classification: `product` / `test` / `environment` / `baseline` / `flaky` / `specification`
- Explanation:

## Change made

| Path | Change | Why minimal |
| --- | --- | --- |

## Regression evidence

| Command/scenario | Exit/result | Evidence |
| --- | --- | --- |

## Scope and risk check

- Unrelated changes:
- New risks:
- Approval needed:

## Decision and next action

- Status: `ready` / `needs-review` / `blocked`
- Next phase:
