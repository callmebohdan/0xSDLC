# Phase protocol

This is the operating procedure shared by every 0xSDLC subagent. The active subagent file adds phase-specific rules; it does not replace this protocol.

## Before acting

1. Confirm the task ID, repository root, current phase, and requested output artifact.
2. Read root `AGENTS.md` when present. If absent, read task-local `project-context.md`; do not invent project commands or conventions.
3. Read the phase contract, the output template, and the listed input artifacts.
4. Inspect the repository state before making assumptions. Check the current branch, working-tree changes, relevant files, and available commands when the phase requires it.
5. Identify the task boundary: what is included, explicitly excluded, and potentially affected indirectly.
6. If a required input is missing, contradictory, stale, or inaccessible, stop with `blocked` or `needs-review` and explain exactly what is needed.

## While acting

- Perform only the assigned phase. Do not silently perform planning, implementation, review, or deployment work belonging to another agent.
- Separate facts, inferences, decisions, and open questions.
- Prefer existing project patterns over new abstractions.
- Make the smallest change that satisfies the current task slice.
- Keep source changes and evidence changes distinguishable.
- Re-check assumptions when an inspection result contradicts the brief or spec.
- Preserve user changes. Never overwrite unrelated edits merely to make the working tree clean.
- Use deterministic commands where possible and record the exact command and exit code.

## Before handing off

1. Compare the result with the phase contract and the relevant acceptance criteria.
2. Run the narrowest meaningful validation available.
3. Record files inspected and changed, commands run, evidence, failures, assumptions, risks, and next action.
4. Use the output template and valid status vocabulary.
5. Check that the next agent can continue without the current chat transcript.

## Stop conditions

Stop instead of guessing when:

- requirements conflict and no priority is stated;
- a proposed action crosses an approval boundary;
- a required command, dependency, credential, service, or fixture is unavailable;
- the test baseline is already failing and the failure cannot be separated from the change;
- the requested behavior would weaken security, data integrity, or backward compatibility;
- the output would require claiming evidence that was not actually obtained.

## Compact handoff formula

Use this order in every report:

`decision → evidence → assumptions → risks → next action`

Do not end with a vague phrase such as “looks good.” State what is proven, what is not proven, and who or what must act next.
