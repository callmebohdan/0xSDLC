# 0xSDLC architecture

## System view

```text
user request
    ↓
autopilot creates brief.md + route.json
    ↓
specify → audit → design → plan → [approval]
                                      ↓
                         implement → test → review ── approve → verify
                                           ↑       │
                                           └─ fix ──┘
```

The standard route is `specify → audit → design → plan → implement → test → review → verify`.
Small work skips specification and design when the request is already bounded. High-risk work inserts a human approval gate before implementation. Quality assurance is an optional release, compliance, or regulated-work gate; it is not a second review for ordinary tasks.

## Repository and runtime boundaries

```text
repository/
├─ 0xSDLC-{autopilot,design,plan,implement,fix,verify}/  regular subagents
├─ support/agents/                                      less-frequent subagents
├─ support/{adapters,conventions,mcp,integrations}/      shared support
├─ templates/                                            artifact schemas
├─ orchestrator/                                         manifest and route metadata
├─ docs/operations/                                      operating procedures
├─ docs/                                                 rationale and reference
└─ scripts/                                              dependency-free tooling

%USERPROFILE%/.agents/0xsdlc/
└─ sessions/YYYY-MM-DD_short-description_XXXXXXXX/       task state and evidence
```

Contracts are versioned in the repository and published as a user-level copy. Generated task state never belongs beside source contracts and is ignored by Git.

## Responsibilities

### Orchestrator

Owns task identity, classification, route selection, phase order, state transitions, adapter invocation, transcripts, artifact presence/metadata checks, bounded recovery, and stop conditions. It records decisions but does not invent product requirements.

### Phase agent

Owns one bounded transformation: specify, audit, design, plan, implement, test, review, verify, or fix. It reads only the relevant inputs, follows shared guardrails, and writes the named artifact. A model response without the artifact is not a completed phase.

### Adapter

Translates a generic prompt packet into a provider-specific CLI or API call. Adapter syntax may vary across Codex, Claude, Cursor, Qwen, Llama, or future providers; artifact schemas, permissions, evidence rules, and state semantics must not vary.

### Human

Owns ambiguous product decisions, high-impact approvals, accepted residual risk, merge/release decisions, and any action reserved by repository policy. Silence is never approval.

## Durable state model

`route.json` is the machine-readable source of orchestration state. Each route contains the request, classification, ordered phases, current phase, overall status, per-phase state, lane results, attempts, timestamps, artifacts, and append-only events.

Allowed phase transitions are:

```text
pending → running → succeeded
                  ├→ blocked
                  ├→ failed
                  └→ needs-approval
succeeded → running       (bounded rerun)
blocked/failed → running  (resume after cause is addressed)
```

The review recovery loop is explicit and bounded: `review(decision: fix) → fix → test → review`. The orchestrator records `fix_attempts`, every repeated phase transition, and a `fix-limit-reached` event. After two unsuccessful attempts, it stops at `needs-review` instead of looping indefinitely.

Approval is also explicit. The high-risk route pauses with `status: needs-approval`; `approve --by ... --scope ...` records the human decision and only then can `resume` continue to implementation. `resume` refuses to bypass an approval or human-review stop.

## Context and cost model

The prompt is layered so every model receives only what it needs:

1. shared boundaries and phase protocol;
2. the active domain contract and output template;
3. brief, route, and listed prior artifacts;
4. relevant source files and narrow command output.

The default is one model call per phase. Parallel audit/review lanes are opt-in because they add calls and their results must be synthesized by the orchestrator/reviewer. Retries are reserved for transient adapter failures; product failures change context through the bounded fix loop.

## Design tradeoffs

- Sequential default: lower token cost, easier debugging, and deterministic handoffs.
- Specialized subagents: smaller context and clearer accountability, with handoff overhead.
- Markdown artifacts: human-readable and vendor-neutral, with schema validation required.
- CLI adapters: low dependency coupling, with provider configuration kept outside contracts.
