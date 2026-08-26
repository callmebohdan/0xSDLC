# Orchestrator

This folder contains the machine-readable agent manifest and design notes for running autopilot. Runtime code lives in `scripts/`; provider contracts live in `support/adapters/`.

## Ownership

- Orchestrator: task IDs, route choice, phase order, artifact paths, status, adapter invocation, and stop conditions.
- Adapter: provider-specific invocation and permission translation.
- Subagent: one phase decision or transformation.
- Human: ambiguous product decisions, high-impact approvals, accepted risks, merge, and release.

The orchestrator must remain deterministic around the model: the model may choose implementation details inside the route, but it does not silently change the route, artifact schema, or approval policy.
