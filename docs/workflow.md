# Workflow for a task

## 1. Start with intent

Run:

```text
python scripts\0xSDLC.py autopilot "Add CSV export to the reports page"
```

The CLI creates `.agents/0xsdlc/sessions/<task-id>/brief.md`, `route.json`, and the first prompt packet. Inspect them before execution. The request is preserved verbatim; the route is a decision record, not hidden behavior.

## 2. Select the route

- Small: isolated, low-risk, obvious validation path.
- Standard: feature or multi-file change requiring a spec, plan, tasks, tests, and review.
- High-risk: security, data, production, public API, migration, deletion, payment, or external side effect.

When uncertain, choose the safer route. You can edit the route before execution if the decision was wrong, but record why.

## 3. Run phases with focused context

For each phase:

1. Read the root instructions and shared conventions.
2. Read the active subagent contract and template.
3. Read only listed task artifacts and relevant source files.
4. Inspect before editing.
5. Perform the phase's one job.
6. Run the narrowest meaningful check.
7. Write the artifact with evidence, assumptions, risks, and next action.

Refresh context at phase boundaries. Do not carry an unbounded transcript forward.

## 4. Implement and test

Implementation should be one task slice, not the entire plan. Testing should establish the baseline, exercise acceptance criteria, classify failures, and preserve unavailable or flaky checks. Review should be independent from implementation whenever practical.

## 5. Handle failure

- Missing input or permission: `blocked`.
- Ambiguous product choice or high-impact approval: `needs-review`.
- Product defect: create a bounded fixer loop.
- Baseline/environment defect: preserve evidence and separate it from the task.
- Repeated failed fix: stop after two attempts for the same finding and request review.

Never skip a phase silently or turn a timeout into success.

## 6. Verify and hand off

Verification maps every acceptance criterion to current evidence. It ends in `verified`, `needs-review`, or `blocked`. The final handoff records changed files, commands, approvals, residual risks, and the exact next action.

## Use-case examples

| Request | Route | Important proof |
| --- | --- | --- |
| Fix a typo | small | diff and relevant docs check |
| Add CSV export | standard | headers, escaping, permissions, empty data, download behavior |
| Rotate production credentials | high-risk | approval, secure handling, rollback, post-change validation |
| Diagnose failing login | standard/high-risk | reproduction first, logs without secrets, regression test |
| Refactor a parser | standard | behavior-preserving fixtures and diff review |
