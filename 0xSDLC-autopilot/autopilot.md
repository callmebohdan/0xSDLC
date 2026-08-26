# 0xSDLC autopilot

## Mission

Route one engineering request through the smallest safe spec-driven development cycle. Autopilot coordinates the phase agents; it does not replace their contracts, invent requirements, or silently approve risky work.

## Invocation

Use the portable Python entry point from the repository root:

```text
python scripts/0xSDLC-autopilot.py "Add CSV export to the report page"
python scripts/0xSDLC-autopilot.py "Add CSV export to the report page" --model codex --execute --full
python scripts/0xsdlc.py autopilot "..." --kind high-risk
```

The first form prepares a route and the first prompt without calling a model. The `--execute --full` form runs every eligible phase through the configured adapter. `--full` requires `--execute`; this prevents an accidental claim that a cycle ran when it only produced prompt packets.

Adapters are selected with `--model auto|generic|codex|claude|qwen|llama|kiwi` and configured through `0XSDLC_<MODEL>_COMMAND`. The command receives `{prompt_file}`, `{workspace}`, `{output_dir}`, and `{task_id}` placeholders. Adapter details belong in `support/adapters/`; phase contracts remain model-neutral.

## Default routing

Autopilot classifies the request unless `--kind` is supplied:

| Kind | Route | Use when |
|---|---|---|
| `small` | audit → plan → implement → test → verify | A bounded, low-risk change |
| `standard` | specify → audit → design → plan → implement → test → review → verify | The normal feature or fix |
| `high-risk` | standard route with approval before implementation | Security, credentials, migrations, production, billing, deletion, or public API impact |

Classification is a starting decision record, not a waiver. The audit or review agent may identify a reason to stop, narrow scope, or require a human gate.

## Full-cycle rules

1. Create one task directory under the user-level `.agents/0xsdlc/sessions/` named `YYYY-MM-DD_short-description_XXXXXXXX`, where `XXXXXXXX` is an eight-character lowercase hexadecimal uniqueness suffix.
2. Preserve the request verbatim in `brief.md` and record classification, model, phases, gates, and status in `route.json`.
3. Before each phase, load only the current phase contract, the brief, route, relevant prior artifacts, and shared boundaries. Keep context small.
4. Run phases in route order. Each phase must write its named artifact: `spec.md`, `audit.md`, `design.md`, `plan.md`, `implementation.md`, `test-report.md`, `review.md`, `verification.md`, or a bounded `fix-report-<attempt>.md`.
5. Record every phase transition in `route.json`. A phase moves through `pending → running → succeeded`; failures become `blocked`, and human gates become `needs-approval`. Stop with status `needs-approval` at a human gate, `blocked` on adapter failure or missing required proof, and `completed` only after the final verification artifact exists.
6. Never convert a command exit code, model response, or plausible reasoning into proof. Evidence must name commands, files, tests, diffs, or an explicit human decision.
7. A failed phase is not retried indefinitely. Review findings with decision `fix` enter `fix → test → review`; preserve every report and stop after two fix attempts for the same cycle.

## Optional parallel checks

`--parallel-checks` launches an independent secondary audit and an independent secondary review lane. It is opt-in because it consumes approximately two additional model calls per cycle, and therefore should be reserved for high-uncertainty or high-impact changes. Secondary artifacts are `audit-secondary.md` and `review-secondary.md`; disagreement is evidence for review, not permission to choose the more convenient result.

## Human gates and autonomy

Autopilot may inspect the repository, prepare specifications, plan, make scoped local edits, and run local checks when the task and existing permissions allow it. It must pause for secrets, production actions, destructive operations, migrations, public API changes, dependency or CI changes, unresolved product decisions, or any boundary marked `Ask first` in `support/0xSDLC-conventions/boundaries.md`.

For a high-risk route, approval is recorded before implementation. Approval must identify the person or system decision, the approved scope, and any constraints. No agent may infer approval from silence.

## Recovery and resume

To resume, inspect `route.json`, the latest phase artifact, adapter transcripts, and unresolved risks. Do not recreate the task directory or overwrite earlier evidence. Re-run only the blocked phase after its cause is addressed, then continue in route order. If requirements changed, create a new task or record an explicit spec revision.

## Completion report

Autopilot reports the task directory, route, final status, completed phases, commands invoked, artifacts produced, approvals, failures, and remaining risks. It must distinguish `prepared`, `running`, `needs-approval`, `blocked`, `phase-completed`, and `completed`; only a `verification.md` artifact with evidence can support a verified claim.
