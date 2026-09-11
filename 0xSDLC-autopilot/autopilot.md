# 0xSDLC autopilot contract

## Mission

Route one engineering request through the smallest safe, evidence-backed development cycle. Autopilot coordinates focused phases; it does not invent requirements, treat model text as proof, or convert a user request into permission for sensitive changes.

## Route rules

| Route | Phases | Use when |
| --- | --- | --- |
| Small | audit → plan → implement → test → review → verify | isolated, reversible work with an existing pattern |
| Standard | specify → audit → [design] → plan → implement → test → review → verify | normal feature, defect, or multi-file change |
| High-risk | specify → audit → design → plan → approval → implement → test → review → verify | security, data, production, public contract, payment, migration, deletion, or other irreversible impact |

The bracketed design phase is a decision record, not ceremony. Include it for architecture, integrations, cross-module behavior, data/control-flow changes, material alternatives, or uncertain compatibility. Omit it when audit and plan can safely describe one obvious local change. The user may force either choice for non-high-risk work; high-risk work always includes design.

Fold intake into `specify`: the brief is captured deterministically and the specifier clarifies outcome, actors, acceptance criteria, boundaries, and unknowns. The legacy intake contract is not part of a normal route.

## Task state

1. Create exactly one directory under `%USERPROFILE%\.agents\0xsdlc\sessions\YYYY-MM-DD_short-description_8hex`.
2. Persist the verbatim request in `brief.md` and route, rationale, phase state, approvals, attempts, and events in `route.json` before any adapter call.
3. Each phase writes the requested Markdown artifact with `task_id`, `phase`, and controlled `status` front matter. A missing or invalid artifact blocks the route.
4. State transitions are recorded atomically. Valid phase states are `pending`, `running`, `succeeded`, `blocked`, `needs-approval`, and `skipped`.
5. Resume from the same directory. Do not recreate or overwrite prior artifacts to make a route appear clean.

Route schema `0.4` and artifact schema `0.2` are current. Existing route `0.2`/`0.3` and artifact `0.1` state remains readable through explicit migration rules. Unknown schema versions stop instead of being guessed into compatibility.

## Execution and stop rules

- Load current phase contract, brief, route, project `AGENTS.md`, listed artifacts, and only relevant source. Do not paste the whole library or conversation into every prompt.
- Run one phase at a time and preserve adapter stdout/stderr. Record commands, paths, result summaries, assumptions, and limitations.
- A phase reports `blocked` when it cannot proceed safely; `needs-review` when a human choice or approval is required. Autopilot stops in both cases.
- For high-risk or explicitly gated work, stop after plan/design. A human approval states scope and constraints; silence is not approval.
- Test proves behavior at a chosen level. Review independently searches for defects and weak evidence. Verify maps each required acceptance criterion to current evidence; neither test nor review alone is final verification.
- Audit, design, or plan evidence may add a safer `design` or `approval` phase. Every accepted route change records its source and reason; agents may not dynamically remove a required gate.
- Full execution owns an exclusive task lock. Resume marks any orphaned `running` phase as interrupted, preserves that event, and retries only through a valid state transition.

## Review and fix loop

`review.md` uses `decision: approve | fix | needs-review`. A `fix` decision must name stable `blocking_findings` IDs. Autopilot runs `fix → test → review`, retaining `fix-report-1.md`, `test-report-1.md`, `review-1.md`, and later attempts rather than overwriting history.

It allows two attempts per stable finding and four attempts per route. If stable IDs are missing, a finding persists past its cap, or the reviewer asks for a human decision, autopilot ends at `needs-review`. It never repeats a product failure with an unchanged prompt.

## Parallel checks

`--parallel-checks` is opt-in. It adds an independent audit lane and review lane, then a separate synthesis call for each pair. The synthesis reconciles disagreement, keeps the stricter evidence-backed conclusion, and records whether the extra call changed confidence. This costs four extra model calls; reserve it for high-impact or high-uncertainty work.

`--maintainability-review` is a narrower opt-in. It adds one focused review lane plus synthesis, costing two extra calls. Use it for reusable libraries, architectural changes, public interfaces, performance/concurrency-sensitive code, or explicit maintainability concerns. It is not a formatting agent: deterministic project tools handle mechanical style. When combined with `--parallel-checks`, all three review reports share one synthesis, for five extra calls across the route rather than six.

## Engineering practices

Project instructions, checked-in tooling, and established local conventions remain authoritative. The runner records a bounded project profile for every task and selectively loads generic maintainability/architecture guidance plus applicable language profiles. It must not inject the entire practice library, impose one company's style guide, or turn a scoped task into a broad cleanup.

## Boundaries

Autopilot may inspect, specify, plan, make scoped local changes, and run local checks when allowed. It pauses for every `Ask before doing` boundary in [`boundaries.md`](../support/0xSDLC-conventions/boundaries.md), including secrets, external data transfer, dependencies, CI/release, migrations, public contracts, destructive operations, and commits. More restrictive project instructions win.

If the target repository has no `AGENTS.md`, create task-local project context from observable files and continue when safe. Use the separate project-bootstrap agent to propose permanent instructions; adopting that draft requires explicit human approval and must never overwrite an existing file automatically.
