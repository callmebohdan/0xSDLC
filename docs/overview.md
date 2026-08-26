# 0xSDLC overview

0xSDLC is a lightweight, model-neutral harness for spec-driven software work. It gives coding agents a durable operating system made of instructions, phase contracts, task artifacts, verification gates, and provider adapters.

It is not a single “super prompt.” Reliability comes from making every important decision inspectable and every completion claim evidence-backed.

## What problem it solves

Coding models are fast at producing output but can lose requirements, invent context, skip verification, overreach into nearby files, or declare success too early. 0xSDLC addresses those failure modes by:

- converting short intent into a durable brief and testable specification;
- giving each subagent one narrow responsibility;
- handing context between phases through files rather than chat history;
- separating implementation from testing, review, and verification;
- making risk and approval boundaries explicit;
- preserving failure evidence and stopping when safe progress is impossible.

## Maturity target

### Level 2 — repeatable assisted engineering

- shared project instructions;
- reusable phase contracts;
- durable Markdown artifacts;
- test/report/review gates;
- provider-neutral adapter boundary.

### Level 3 — bounded autopilot

- automatic risk classification;
- route selection;
- task folders and prompt packets;
- stop conditions and human gates;
- independent evaluator phases;
- bounded fix loops.

### Future level 4 work

Do not add these merely because they sound advanced. Add them after real task evidence justifies them:

- policy-enforced tool permissions;
- parallel worktrees and conflict-aware merging;
- conformance suites generated from specs;
- telemetry, cost budgets, and model routing;
- resumable multi-phase execution;
- provider health checks and cancellation.

## Supported work types

| Work type | Typical route | Special concern |
| --- | --- | --- |
| Small local fix | small | avoid over-process; still verify behavior |
| New feature | standard | define user journeys and failure behavior |
| Bug diagnosis | audit → test/review | separate reproduction from fix |
| Refactor | audit → plan → implement → test → review | preserve behavior and compare diff |
| Security/auth/data change | high-risk | explicit approval and threat review |
| Documentation-only change | small or standard | source of truth and freshness |
| Production/deployment change | high-risk | rollback, blast radius, human gate |

## Source and runtime locations

- Root-level `0xSDLC-*`, `support/adapters/`, `templates/`, and `support/0xSDLC-conventions/`: versioned source contracts in this repository.
- user-level `.agents/0xsdlc`: published copy for model CLIs that need a global location.
- `.agents/0xsdlc/sessions/`: generated task briefs, prompts, reports, and adapter transcripts.
- `scripts/`: dependency-free orchestration, installation, and validation utilities.
- `docs/`: design rationale and rollout guidance.

## Core principle

Use the least complex route that can prove the requested behavior. More agents are not automatically more reliable; clear boundaries, relevant context, and independent evidence matter more.
