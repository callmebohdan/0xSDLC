# Sessions and output

Session storage uses `--sessions-root`, then `0XSDLC_SESSIONS_ROOT`, then `<project-root>/.agents/0xsdlc/sessions`. The project root is the Git root containing the workspace; outside a Git repository, it is the workspace directory. Relative overrides resolve from the current directory. Contracts, templates, and provider profiles still resolve from the user-level runtime library (`~/.agents/0xsdlc` by default), which is separate from project sessions.

When a task ID is used without an explicit session-root override, lookup checks the current project's session directory first, existing project-specific directories directly under `logs/` next, and the legacy user-level session directory last (`<0XSDLC_AGENTS_HOME>/sessions` if configured, otherwise `~/.agents/0xsdlc/sessions`). This keeps tasks created with the previous `logs/<project-name>` convention discoverable. `status` lists these locations. Pass `--sessions-root` or the full task directory when resuming a task from another project. New tasks always use the project-local default unless an override is set.

Pass the same override to `autopilot`, `resume`, `status`, `bootstrap`, or `native` when using a task ID. `resume`, `native`, and `bootstrap --adopt` also accept the full task directory. The runner checks that it can create and atomically replace files before executing. In a restricted workspace, select a writable directory and verify that Git ignores it before storing private evidence.

## Layout

```text
<sessions-root>/<task-id>/
  brief.md
  route.json
  prompt-<first-phase>.md
  <phase reports>.md
  calls/<call-id>.json
  attempts/<attempt-id>/<call-id>/<adapter prompt, logs, sidecar>
  attempts/<attempt-id>/<native phase prompt>
  metrics.jsonl
```

Keep one task's evidence together. Never overwrite a failed report to make the task appear green. Redact secrets and private data from artifacts before sharing them. The eight-character suffix prevents collisions while keeping paths readable.

The runner uses an OS lock on the persistent `.0xsdlc.guard` file. It releases when the owning process exits. On upgrade, finish any run started by the previous runtime before reopening its session. `resume --stale-lock-seconds` sets the minimum age for recovery of a legacy `.0xsdlc.lock` whose local owner has exited.

## Native chat

Use the local Python runner from the repo or installed runtime. The default session directory is already covered by the repository's `.agents/` ignore rule.

```text
python scripts/0xSDLC.py autopilot "<request>" --native
python scripts/0xSDLC.py native open "<task-directory>" <phase>
python scripts/0xSDLC.py native close "<task-directory>" <attempt-id> --outcome succeeded
```

Open each phase before working on it. Read the returned prompt and write the phase report to the returned artifact path before closing it. `close` validates the artifact and supports `succeeded`, `failed`, `blocked`, and `needs-review`. A verification phase succeeds only with `status: verified`. Use `autopilot --native --phase <phase>` for a standalone, authorized phase. `resume --approve` and `resume --resolve-review` record explicit human decisions. Native test or review findings that need repair stop at `needs-review` for human resolution.

Close on the same host and clock epoch. If the phase was abandoned or its clock is unavailable, run `native interrupt "<task-directory>" <attempt-id>` before retrying. The interruption records recovery time separately and leaves the actual finish and elapsed time unknown. Native attempts store unavailable adapter and provider metrics as `null`.

## Reading telemetry

- `route.json` stores every phase attempt under `phase_states.<phase>.attempt_history`. An attempt has an ID, UTC start/end, monotonic wall duration, outcome, report paths, call IDs, and Git HEAD at the phase boundaries when available. Git HEAD identifies the commit. It does not attest to a clean working tree.
- `metrics.jsonl` lists adapter calls by ID. Each record links to its phase attempt and evidence paths and records adapter wall time, provider inference time when reported, outcome, and usage. Synthesis links to the same attempt as its parallel lanes. Parallel lane selection persists on resume. Phase wall time includes validation and synthesis. The sum of call durations can exceed phase wall time when calls overlap.
- The route summary reports known totals and `coverage`, the count of calls contributing to each field. `calls` counts started dispatches, including interrupted calls. A missing metric is `null`. A measured zero contributes to coverage. Cost and usage carry their reported source.
- The call journals are written atomically and can rebuild the summary on resume. Legacy JSONL entries without call IDs are preserved and legacy aggregates are kept under `legacy_telemetry`. Historical values with no coverage or reliable call IDs are excluded from new totals. Recovered interruptions carry `provenance: retrospective`; a standalone retrospective report should declare `execution: retrospective` or `resumable: false` and cannot be resumed as a route.
