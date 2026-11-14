# AI readiness assessment

## Current position

0xSDLC is a structured L2 harness with early L3 capabilities. It has phase contracts, durable artifacts, model-neutral adapters, risk-based routing, explicit approval gates, structured route state, and bounded fix loops.

## Readiness dimensions

| Dimension | Current capability | Remaining gap |
| --- | --- | --- |
| Specification | brief/spec artifacts and acceptance criteria | automated criterion linting |
| Planning | design and implementation plan contracts | dependency/DAG validation |
| Execution | provider command adapters and scoped phase prompts | provider health, cancellation, and time budgets |
| State | atomic route writes with backups, exclusive per-task lock, phase/event records, interrupted-run recovery, durable approvals, resume command | lease-based multi-host ownership, cancellation, and recovery across external workers |
| Verification | separate test, review, and verify phases, artifact metadata checks | independent evaluator quality checks and criterion linting |
| Recovery | bounded fix → test → review loop for stable test/review findings, per-finding and total attempt caps, numbered evidence | finding deduplication and automatic regression-test synthesis |
| Cost control | minimal default route, opt-in parallel lanes/quality gate, call counts and optional token/cost sidecars | enforced token/call budgets and cancellation |
| Safety | human gates and evidence rules | policy-enforced tool permissions |

## Evaluation evidence so far

The available evidence has two different strengths: captured runner artifacts for verification-only sessions, and retrospective outcome evidence from real AWEAR work in other chats. The latter is useful for quality and workflow conclusions even when exact phase timing is unavailable.

### Captured runner evidence

Two completed verification-only sessions from 2026-11-10 both ended `verified`. They evaluated 0xSDLC mechanics rather than representative application changes.

| Evidence | Session A | Session B |
| --- | --- | --- |
| Scope | telemetry, retry/resume, parallel lanes, and native recorder handover | verification completion gate and task locking |
| Result | verified; 43-test discovery run passed after scoping TEMP/TMP to the repo | verified; 47-test discovery run and five focused tests passed |
| Verify-phase wall time | 10m 31s | 2m 35s |
| Provider evidence | deterministic fake-adapter tests; no live-provider conformance | deterministic fake-adapter tests; POSIX lock path not exercised |

Both route summaries recorded `calls: 0`, with no provider, token, or cost measurements. Those values mean the native sessions did not capture adapter-call telemetry; they do **not** establish zero model usage or cost. The phase durations are not a performance comparison: task scope differed and native wall time includes interactive work. A separate prepared-only task has no completed phases and is excluded.

### Retrospective real-task outcomes

Other chats provide outcome evidence from AWEAR implementation work:

| Work stream | Observed outcome | Limitation |
| --- | --- | --- |
| PoC implementation | Typecheck, production build, four fit tests, HTTP flow, and persistence/restart checks passed after switching from Turbopack to Webpack when Windows junction permissions caused EPERM. | The workaround was environment-specific; complete phase-level AI timing and cost are unavailable. |
| Scanner parity | 18/18 tests, typecheck, and code review passed. Build hit EPERM and browser access was blocked, so the session correctly remained `needs-review`; visual verification was not completed. | We cannot attribute the environment failures to 0xSDLC itself or measure time spent resolving them. |
| Wardrobe/purchase parity | 23 tests, typecheck, production build, and diff check passed. | Calendar validation remained open; no screenshots were captured, so visual parity was not claimed. |

These records show useful functional progress and that incomplete visual/environment checks were not reported as verified. They also show repeated Windows EPERM friction and missing visual evidence. Most phase boundaries and durations, provider inference time, token usage, and cost were not recorded; later UI refinement also happened outside separate Autopilot tasks. Treat these as retrospective outcomes, not captured runner metrics. A planned profile/color-test handover has no implementation result and is excluded.

Together, the evidence supports these conclusions:

- Outcome data from other chats is valid for evaluating acceptance results, test/build results, review disposition, human follow-up, and environment blockers.
- Phase timings are useful for locating time sinks and comparing route changes, but are not required to evaluate correctness or workflow quality.
- The current data is still insufficient to compare provider health, cancellation, budget behavior, repeated-finding handling, criterion quality, or cross-provider equivalence.

## Prioritized L3 backlog

### Priority 1 — Close the outcome and evidence baseline

The other-chat evidence broadens the baseline beyond two phase timings. Keep adding naturally occurring real-task sessions until there are at least five distinct outcomes, counting incomplete and environment-blocked work. Include a bug fix, a small feature, and a diagnosis/read-only task when available; include repair or resume cases if they naturally occur. Do not manufacture risky tasks to fill the set. The repeated EPERM/browser-verification friction is the clearest observed workflow issue to track, but it is not yet enough to justify a broad environment-specific feature.

For each session, record task class and repository, execution mode/provider when known, expected outcome and acceptance result, test/build/review results, blocked or unavailable checks, human interventions, and repeated findings. Record phases, wall time, attempts, and call/token/cost data when captured; otherwise mark them unknown and label the record retrospective. Never infer precise timings from chat ordering or treat missing usage as zero. Include failed, incomplete, and abandoned attempts so the baseline does not contain only successful runs.

### Priority 2 — Select one feature from observed failure signals

The current baseline does not justify choosing among these candidates. Rank them after the baseline by severity and frequency of observed impact:

| Candidate | Promote when real-task evidence shows |
| --- | --- |
| Provider health and cancellation | stalled, unavailable, or non-cancellable provider calls repeatedly block progress or recovery |
| Budget enforcement | measured calls, tokens, cost, or elapsed time exceed explicit per-task limits |
| Finding deduplication | the same underlying review/test finding is reapplied or retried as if it were new |
| Criterion linting | ambiguous or untestable acceptance criteria cause rework, disagreement, or false completion |
| Cross-provider conformance | provider portability is needed and the same task packet produces materially different or invalid artifacts across live providers |

Until a trigger appears, keep these as hypotheses rather than committed implementation priorities. The existing deterministic fake-adapter suite is useful for regression coverage, but it cannot answer live-provider portability or spend questions.

## Design principles

1. Make the route deterministic and the model's decisions inspectable.
2. Let artifacts carry state across context resets; do not depend on chat memory.
3. Use the least expensive model and shortest route that can prove the criterion.
4. Treat disagreement as a signal to pause or synthesize, never as permission to choose the convenient answer.
5. Keep high-impact actions behind explicit human approval.

## L2 completion criteria

The harness satisfies the practical L2 bar: every phase has a clear input/output contract, artifact metadata is checked, failure states are visible, the normal route is cost-bounded, and a fresh agent can resume from the task directory without replaying the conversation. It is early L3 because route selection, approval, bounded recovery, and optional parallel checks exist, but policy enforcement and measured runtime controls are not yet complete.

Atomic replacement, single-task locking, interruption marking, deterministic fake-adapter scenarios, and bounded fix IDs already exist; do not report those foundations as missing.
