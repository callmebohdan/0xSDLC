# 0xSDLC architecture

## System view

```text
user request
    ↓
intake / route classifier
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

Owns one bounded transformation: specify, audit, design, plan, implement, test, review, verify, or fix. Quality assurance remains an optional release/compliance gate, not a default phase. Each agent reads listed inputs, follows shared guardrails, and writes the named output artifact.

### Adapter

Translates a generic prompt packet into a provider-specific CLI or API call. It may change invocation syntax and tool names, but must not change boundaries, artifact schemas, or status semantics.

### Human

Owns ambiguous product decisions, high-impact approvals, accepted residual risks, merge/release decisions, and any action the repository policy reserves for a person.

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
prepared → running → artifact-ready
                    ↘ blocked
                    ↘ needs-review
                    ↘ failed
artifact-ready → next phase
verification → verified | needs-review | blocked
```

State changes must be reflected in the route/artifact and supported by evidence. A model response without a durable artifact is not a completed phase.

## Design tradeoffs

- Sequential default: lower coordination cost and easier debugging.
- Specialized subagents: smaller context and clearer accountability, at the cost of handoff overhead.
- Markdown artifacts: human-readable and model-portable, at the cost of requiring disciplined templates.
- CLI adapters: low dependency coupling, at the cost of provider-specific configuration and weaker runtime introspection.
