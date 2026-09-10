---
schema_version: "0.2"
task_id: "{{task_id}}"
phase: "design"
status: "ready"
agent: "architect"
inputs: ["brief.md", "spec.md", "audit.md"]
assumptions: []
---

# Technical design

## Decision summary

- Problem and constraints:
- Chosen approach:
- Why this is the smallest safe approach:
- Non-goals:

## Architecture and flow

1. Entry point:
2. Main data/control flow:
3. State and persistence:
4. Error, retry, and rollback behavior:
5. Observability and operational impact:

## Alternatives

| Option | Benefit | Cost/risk | Decision |
| --- | --- | --- | --- |

## Boundaries and risks

- Security/privacy:
- Compatibility/public contracts:
- Performance/concurrency:
- Migration/deployment:
- Human approval required:

## Evidence and handoff

- Repository evidence:
- Design decisions requiring confirmation:
- Test strategy:
- Next phase: `plan`
