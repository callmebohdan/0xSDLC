# Evidence and status standard

0xSDLC treats evidence as a first-class output. A claim is not evidence merely because a model believes it.

## Evidence quality

Strong evidence is:

- reproducible by another agent or developer;
- tied to a file, command, test case, diff, log, screenshot, or explicit decision;
- current for the implementation being evaluated;
- scoped to the criterion it proves;
- clear about limitations and environment assumptions.

Weak evidence includes “implemented,” “reviewed,” “should work,” an unrun command, a pasted code fragment without execution, or a green test that does not exercise the requested behavior.

## Command records

For every meaningful command, record:

| Field | Example |
| --- | --- |
| Command | `pytest tests/test_export.py -q` |
| Working directory | repository root |
| Exit code | `0` |
| Result | 12 passed |
| Limitations | external service mocked |

Do not include secrets in command lines or reports. Redact tokens, cookies, private paths, and personal data.

## Status decision rules

Use `ready` when the phase output is complete and its known limitations do not block the next phase.

Use `needs-review` when a human must choose between valid options, approve a high-impact action, resolve a product ambiguity, accept a known risk, or decide whether a baseline failure is in scope.

Use `blocked` when the phase cannot be completed safely or honestly because a required input, permission, tool, fixture, or environment capability is missing.

Use `verified` only in `verification.md`, after every required acceptance criterion has a current evidence entry and no unresolved blocker remains. Passing tests alone does not imply `verified`.

## Failure classification

Classify failures as one of:

- `product`: the implementation violates the spec;
- `test`: the test is incorrect, incomplete, or too brittle;
- `environment`: dependency, platform, network, service, or permission problem;
- `baseline`: pre-existing failure reproduced before the change;
- `flaky`: non-deterministic result requiring repeated observation;
- `specification`: ambiguous or contradictory requirement.

Never hide a failure by deleting a test, loosening an assertion, suppressing output, or changing the status without explaining why.
