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

## Design principles

1. Make the route deterministic and the model's decisions inspectable.
2. Let artifacts carry state across context resets; do not depend on chat memory.
3. Use the least expensive model and shortest route that can prove the criterion.
4. Treat disagreement as a signal to pause or synthesize, never as permission to choose the convenient answer.
5. Keep high-impact actions behind explicit human approval.

## L2 completion criteria

The harness satisfies the practical L2 bar: every phase has a clear input/output contract, artifact metadata is checked, failure states are visible, the normal route is cost-bounded, and a fresh agent can resume from the task directory without replaying the conversation. It is early L3 because route selection, approval, bounded recovery, and optional parallel checks exist, but policy enforcement and measured runtime controls are not yet complete.

## L3 backlog

Prioritize multi-host leases/cancellation, enforceable measured budgets, evaluator quality and real-project baselines, review-finding deduplication, and stronger synthesis of parallel lanes before adding more agents or providers. Atomic replacement, single-task locking, interruption marking, deterministic fake-adapter scenarios, and bounded fix IDs already exist; do not report those foundations as missing.
