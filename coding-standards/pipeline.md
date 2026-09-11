# Harness pipeline standard

Every task must have a visible path from request to evidence:

`specification → audit → design → plan → implementation → test → review → verify`

For a review finding, use the bounded recovery loop:

`review → fix → test → review`

Quality assurance is an optional release, compliance, or high-risk gate rather than a default phase.

## Gate rules

- A phase cannot advance without its required artifact.
- A failed check is preserved and classified.
- A human gate cannot be replaced by a model confidence statement.
- Verification must map every acceptance criterion to evidence.
- Fixes must reference the original finding and include regression evidence.

## Context rules

- Load root instructions, shared conventions, active phase instructions, current artifacts, and relevant source only.
- Start a fresh context at major phase boundaries.
- Use task artifacts as handoffs, not a full conversation transcript.
- Load only phase-relevant engineering practices and detected language profiles. Project configuration and local conventions take precedence.

## Engineering-quality rules

- Audit discovers formatter, linter, compiler, static-analysis, sanitizer, test, language-version, and architecture evidence.
- Design justifies interfaces, boundaries, ownership, relevant scalability, and every new pattern or abstraction.
- Implementation follows deterministic project tooling and avoids unrelated style cleanup.
- Review reports maintainability defects only when backed by project policy or concrete correctness, coupling, ownership, testability, performance, or operational impact.
- Use the optional maintainability review lane only when its two extra calls can materially change the decision.

## Failure rules

- Missing input or permissions: blocked.
- Product ambiguity or high-impact choice: needs-review.
- Product defect: bounded fix loop.
- Environment failure: preserve and classify; do not distort product code.
- Two failed fixes for the same finding: human review.
