---
schema_version: "0.2"
task_id: "{{task_id}}"
phase: "audit"
status: "ready"
agent: "auditor"
inputs: ["brief.md", "spec.md"]
assumptions: []
risk_level: "low" # low | medium | high
route_add: [] # optional: design, approval
route_reason: ""
---

# Repository audit

<!-- This is an evidence map, not a design proposal. Cite paths and commands. Do not edit source in this phase. -->

## Repository state

- Root:
- Branch:
- Working-tree changes before task:
- Runtime/platform:
- Relevant instruction files:

## Relevant structure

| Area | Paths | What was found | Relevance |
| --- | --- | --- | --- |
| Source | | | |
| Tests | | | |
| Configuration | | | |
| Data/schema | | | |
| Docs/generated | | | |

## Existing behavior and extension points

- Current behavior:
- Likely entry point:
- Callers/consumers:
- State/persistence:
- External services:
- Trust boundaries:

## Existing commands and baseline

| Purpose | Command | Working directory | Exit code | Result / limitation |
| --- | --- | --- | ---: | --- |
| Install | | | | |
| Build/type-check | | | | |
| Test | | | | |
| Lint/format | | | | |
| Static analysis/sanitizers | | | | |

## Conventions to preserve

- Naming and structure:
- Error handling:
- Logging/observability:
- Test style/fixtures:
- Dependency policy:
- Generated files:
- Language version/toolchain:
- Formatter/linter/compiler configuration:
- Architecture/dependency conventions:

## Risks and unknowns

| ID | Risk/unknown | Evidence | Impact | Owner/next action |
| --- | --- | --- | --- | --- |

## Audit conclusion

- Baseline status: `green` / `failing` / `not-run` / `blocked`
- Files safe to change:
- Files requiring approval:
- Recommended next phase:
