# 0xSDLC architecture

## System view

```text
user request
    ↓
route classifier + deterministic brief
    ↓
.agents/0xsdlc/sessions/<task-id>/route.json + brief.md
    ↓
focused phase prompt
    ↓
model adapter → subagent → source change or phase artifact
    ↓                              ↑
test → review → fix → test → review → verify ┘
```

## Responsibilities

### Orchestrator

Owns task identity, artifact locations, route choice, phase order, current status, adapter invocation, stdout/stderr capture, and stop conditions. It should not make product decisions hidden inside Python code.

### Subagent contract

Owns one bounded transformation: specify, audit, design, plan, implement, test, review, verify, or fix. Quality assurance remains an optional release/compliance gate, not a default phase. Design is conditional, not a mandatory ceremony. Each agent reads listed inputs, follows shared guardrails, and writes the named output artifact.

### Adapter

Translates a generic prompt packet into a provider-specific CLI or API call. It may change invocation syntax and tool names, but must not change boundaries, artifact schemas, or status semantics.

### Human

Owns ambiguous product decisions, high-impact approvals, accepted residual risks, merge/release decisions, and any action the repository policy reserves for a person.

## Runner modules

The canonical public entry point is `scripts/0xSDLC.py`. Internal responsibilities are separated under `scripts/sdlc_core/`: CLI/workspace resolution, routing/migration, artifact validation, atomic storage/locking, prompt assembly, provider profiles, execution, telemetry, and project bootstrap. This is an internal boundary, not a requirement for provider adapters.

## Why files instead of shared memory

Files are inspectable, versionable, portable across model vendors, and cheap to load selectively. `.agents/0xsdlc/sessions/<task-id>/` is a context-reset boundary: a fresh model can resume from evidence without replaying a long conversation.

## Context layering

| Layer | Contents | Loaded when |
| --- | --- | --- |
| Global | published `~/.agents/0xsdlc` contracts | adapter setup / shared rules |
| Project | root `AGENTS.md`, local conventions | every phase |
| Phase | one subagent contract and template | active phase |
| Task | brief, route, relevant reports | current task |
| Source | only relevant files and tests | needed for decision |

Never substitute a global contract for project-specific instructions. Project rules can be stricter.

## State transitions

```text
pending → running → succeeded → next phase
                 ↘ blocked
                 ↘ needs-approval

review(fix) → fix → test → review
review(needs-review) → human decision
verification → completed | needs-review | blocked
```

State changes must be reflected atomically in `route.json` and supported by a valid artifact. A model response without a durable artifact is not a completed phase. Parallel audit/review lanes add a distinct synthesis artifact before their conclusions influence routing.

## Design tradeoffs

- Sequential default: lower coordination cost and easier debugging.
- Specialized subagents: smaller context and clearer accountability, at the cost of handoff overhead.
- Markdown artifacts: human-readable and model-portable, at the cost of requiring disciplined templates.
- CLI adapters: low dependency coupling, at the cost of provider-specific configuration and weaker runtime introspection.
