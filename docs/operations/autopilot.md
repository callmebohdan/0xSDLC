# Autopilot workflow

Autopilot is a bounded decision loop. It chooses a minimum safe route, creates durable artifacts, and may invoke a configured model adapter. It is not blanket permission to edit code, access production, or declare success.

## CLI modes

From the repository root, prepare a task without invoking a model:

```text
python scripts/0xSDLC-autopilot.py "Add CSV export to the reports page"
```

After reviewing the generated brief and route, run the complete route through the selected adapter:

```text
python scripts/0xSDLC-autopilot.py "Add CSV export to the reports page" --model codex --execute --full
```

`--full` is deliberately opt-in and requires `--execute`. The runner stops at approval gates, adapter failures, or missing required phase artifacts. The detailed agent contract is [`0xSDLC-autopilot/autopilot.md`](../../0xSDLC-autopilot/autopilot.md).

## Inputs

- A concise user request.
- The repository root and its project instructions.
- Available local commands and provider adapters.
- Optional user-supplied constraints such as stack, deadline, compatibility, or approval policy.

If the request is only a symptom (“it is broken”), autopilot may audit and diagnose, but must not invent a desired behavior. If the request is dangerously broad (“rewrite everything”), classify it as high-risk or ask for a bounded outcome.

## Route selection

### Small route

Use when the task is isolated, low-risk, has an obvious existing pattern, and can be validated locally without changing a public contract.

`audit → plan → implement → test → review → verify`

Examples: a typo, a focused unit test, a local error-message correction, or a small refactor with unchanged behavior.

### Standard route

Use when the task affects several files, has incomplete acceptance criteria, touches an integration point, or needs independent review.

`specify → audit → design → plan → implement → test → review → verify`

Examples: a new feature, a UI/API change, a persistent setting, or a cross-module refactor.

### High-risk route

Use when the task involves security, authentication, secrets, production, deployment, payments, migrations, deletion, public APIs, privacy, or irreversible data changes.

`specify → audit → design → plan → approval → implement → test → review → verify`

The approval phase must name the exact action, blast radius, rollback plan, and evidence required. “User asked for it” is not a substitute for an explicit approval record when the requested action is high-impact.

## Decision algorithm

1. Create a unique task folder under `.agents/0xsdlc/sessions/<task-id>/`.
2. Preserve the user's request verbatim in `brief.md`; do not silently reinterpret it.
3. Identify actors, outcome, affected assets, data sensitivity, external side effects, and reversibility.
4. Classify risk using the route rules above. If uncertain, choose the safer route.
5. Write `route.json` before calling a model. Include classification, phases, gates, model, and current phase.
6. Generate a prompt packet containing only the active contract, required artifacts, relevant project instructions, and the route.
7. Run one phase at a time. Persist its output before starting the next phase.
8. On `blocked` or `needs-review`, stop. Do not automatically skip the phase.
9. On a failed test or review finding, create a bounded fix loop. Reproduce the finding before changing code.
10. If review returns `fix`, run `fix → test → review` and preserve each bounded fix report. End with `verification.md` and a final status of `verified`, `needs-review`, or `blocked`.

## Retry and loop limits

- Retry an adapter only for a transient infrastructure failure, and record the retry.
- Do not repeat an identical prompt after a product failure; change the context, task slice, or contract.
- After two unsuccessful fixes for the same finding, stop for human review.
- Never turn a timeout into success.
- Never advance because a model returned text; advance because the required artifact and evidence exist.

## Autopilot stop conditions

Stop immediately when a model requests secrets, proposes an unapproved destructive action, encounters contradictory requirements, cannot access required evidence, or attempts to modify files outside scope. Write the failure or blocker into the current artifact.

## Human interaction points

Autopilot may proceed without asking for low-risk inspection, planning, local edits, and local tests within scope. It must pause for the `Ask first` boundaries in `support/conventions/boundaries.md`, unresolved product choices, and any high-risk route approval.

## Example route decision

Request: “Add CSV export to the reports page.”

- Likely route: standard.
- Questions: format, authorization, maximum dataset, escaping, filename, and existing export conventions.
- Required proof: acceptance tests for headers, values, empty data, escaping, permissions, and a usable download.
- Not enough: “the button appears” or “the endpoint returns 200.”
