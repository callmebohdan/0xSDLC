# 0xSDLC agent library

The root-level 0xSDLC folders are the source-of-truth contract library for 0xSDLC. They are kept in the repository so they can be reviewed, versioned, and changed with the harness. `scripts/install.py` publishes a copy to the user-level `.agents/0xsdlc` directory for model CLIs that need a globally accessible instruction library.

The library is deliberately model-neutral. A provider adapter may translate these files into Claude, Codex, Cursor, Qwen, Llama, or another model's native format, but it must not change the meaning of the contracts.

## How to use the library

The orchestrator and every model session should load only the smallest useful context:

1. Read the repository's root `AGENTS.md` when present. Otherwise use the task-local project context and consider the bootstrap agent for recurring work.
2. Read `support/0xSDLC-conventions/phase-protocol.md` and `support/0xSDLC-conventions/boundaries.md` once for the current task.
3. Read the current subagent contract from the relevant root-level `0xSDLC-*` folder.
4. Read the current task brief and only the artifacts listed by that contract.
5. Read the relevant template in `templates/` before writing the output artifact.
6. Read `support/0xSDLC-conventions/evidence-and-status.md` before declaring a result.

Do not paste the entire library into every prompt. The common contracts are reusable rules; the phase contract is the active instruction; the task artifacts are the current state.

## Phase map

| Phase | Agent | Primary question | Required output |
| --- | --- | --- | --- |
| Specify | `specifier` | What outcome, boundary, and observable behavior define success? | `spec.md` |
| Discover | `auditor` | What does this repository already provide? | `audit.md` |
| Design | `architect` | What is the smallest safe technical design? | `design.md` |
| Plan | `task-planner` | What are the smallest verifiable implementation slices? | `plan.md` |
| Implement | `implementer` | How do we change one slice safely? | code + `implementation.md` |
| Test | `tester` | Does the change behave correctly and regress safely? | `test-report.md` |
| Review | `reviewer` | What could still be wrong, risky, or out of contract? | `review.md` |
| Verify | `verifier` | Can every acceptance criterion be proven? | `verification.md` |
| Fix | `fixer` | What is the smallest evidence-backed correction? | `fix-report.md` |

The default workflow is sequential. `brief.md` is created deterministically, so intake is folded into specification rather than run as a default model phase. Parallel audit/review is opt-in and requires a separate synthesis artifact; implementation work may be parallel only with non-overlapping files or separate workspaces.

## Artifact rules

- Artifacts are durable state, not a transcript of hidden reasoning.
- Every artifact names its inputs, assumptions, status, evidence, risks, and next action.
- A missing artifact is a blocker, not an invitation to reconstruct facts from memory.
- A stale artifact must be marked stale and regenerated; do not silently reuse it.
- A model may summarize reasoning, but must not include private chain-of-thought, credentials, tokens, or unnecessary personal data.

## Status vocabulary

- `ready`: the artifact is complete enough for the next phase.
- `needs-review`: a human decision, ambiguity, or high-impact approval is required.
- `blocked`: safe progress is impossible with the current inputs, permissions, or environment.
- `verified`: reserved for final verification after every required criterion has evidence.

## Context budget rules

- Prefer a short index plus targeted sections over a complete document dump.
- Carry decisions and evidence forward, not conversational history.
- Refresh the context at phase boundaries or when the current task changes.
- If a model cannot fit the required context, reduce the task slice or create a summary artifact; do not omit a safety-critical constraint.

## Definition of a reliable phase

A phase is reliable when another model can start from its inputs and reproduce the decision or continue the work without asking, “What did the previous agent mean?” The output must be specific enough to guide the next action and honest enough to expose uncertainty.
