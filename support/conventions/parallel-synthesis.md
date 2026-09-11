# Parallel evidence synthesis

This contract applies only after an opt-in secondary audit or review lane has completed. It is deliberately a separate model call: two independent reports are inputs, not a decision by themselves.

## Inputs

- The primary and secondary artifacts named by the prompt packet.
- The task brief, route, relevant specification, and project instructions.
- No fresh source edits. Run a new command only when it is necessary to resolve a stated conflict, and record it.

## Procedure

1. Compare both reports against the same acceptance criteria and evidence.
2. Identify agreements, disagreements, duplicated findings, and evidence that is stale or unsupported.
3. Preserve the stricter conclusion when evidence is incomplete; do not average severity or choose the convenient report.
4. For a review synthesis, set `decision: approve`, `fix`, or `needs-review`. If `fix`, include stable `blocking_findings` IDs copied from the reviewed report or assigned once with an explanation.
5. State whether the extra lane materially changed confidence. If it did not, record that it was redundant so future routes can avoid the cost.

## Output

Write the requested `*-synthesis.md` artifact with front matter:

```yaml
---
schema_version: "0.2"
task_id: "actual-task-id"
phase: "synthesis"
status: "ready"
source_phase: "audit-or-review"
inputs: ["primary.md", "secondary.md"]
decision: "approve" # required only for review synthesis
blocking_findings: [] # required when review decision is fix
---
```

Include: scope, reconciled findings, decision, evidence limitations, cost/value observation, and next action. A synthesis must never make code changes or silently erase a finding.
