# AI readiness assessment

## Current position

0xSDLC is a structured L2 harness with early L3 capabilities. It has phase contracts, durable artifacts, model-neutral adapters, risk-based routing, explicit approval gates, structured route state, and bounded fix loops.

## Readiness dimensions

| Dimension | Current capability | Remaining gap |
| --- | --- | --- |
| Specification | brief/spec artifacts and acceptance criteria | automated criterion linting |
| Planning | design and implementation plan contracts | dependency/DAG validation |
| Execution | provider command adapters and scoped phase prompts | provider health, cancellation, and time budgets |
| State | route status, phase status, attempts, events, approval records, resume command | atomic writes, locks, and crash recovery |
| Verification | separate test, review, and verify phases, artifact metadata checks | independent evaluator quality checks and criterion linting |
| Recovery | bounded fix → test → review loop with per-finding and total attempt caps | finding deduplication and automatic regression-test synthesis |
| Cost control | minimal default route and opt-in parallelism with documented call costs | measured token/call budgets and cancellation |
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

Prioritize atomic crash-safe resume, deterministic fake-adapter tests, measurable call/token budgets, review-finding IDs, and stronger synthesis of parallel lanes before adding more agents or providers.
