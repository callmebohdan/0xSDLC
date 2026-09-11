---
schema_version: "0.1"
task_id: "{{task_id}}"
phase: "handoff"
status: "ready"
agent: "autopilot"
inputs: ["brief.md", "spec.md", "implementation.md", "test-report.md", "review.md", "verification.md"]
assumptions: []
---

# Pull-request proposal

## Title

<!-- Imperative, concise, and specific. Do not claim verification in the title. -->

## Summary

- Why this change is needed:
- What changed:
- What is deliberately not changed:

## Scope

- Branch:
- Commit(s):
- Changed files:
- Related issue or task:

## Validation

| Command or scenario | Result | Evidence |
| --- | --- | --- |

## Risk and operations

- Security/privacy impact:
- Compatibility or migration impact:
- Performance/operability impact:
- Rollback plan:
- Known limitations or follow-ups:

## Approval and handoff

- Human approval required:
- Approval evidence:
- Reviewer focus:
- Generated artifact directory:

## Checklist

- [ ] Diff is limited to the approved scope.
- [ ] No secrets, credentials, generated sessions, or private transcripts are included.
- [ ] Tests and checks are recorded with their actual results.
- [ ] Review findings are resolved or explicitly carried forward.
- [ ] Verification maps the acceptance criteria to evidence.
- [ ] Remote Git action is still pending unless explicitly authorized.
