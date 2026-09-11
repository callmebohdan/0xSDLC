# Maintainability review lane

## Mission

Independently assess whether the changed design remains understandable, reusable where reuse is real, testable, scalable along relevant dimensions, and economical to maintain. This lane supplements the correctness/security review and does not edit source.

## Inputs

- Specification, audit, design, plan, implementation, test report, and current diff.
- Repository instructions and checked-in style/tool configuration.
- Applicable engineering-practice and language supplements in this packet.

## Procedure

1. Identify the responsibilities and dependencies changed by the task.
2. Check cohesion, coupling, dependency direction, interfaces, ownership, state, errors, concurrency, and test seams.
3. Evaluate only scalability dimensions named by requirements or supported by repository evidence.
4. For every new pattern or abstraction, verify the concrete problem, alternatives, consequences, and current consumers.
5. Distinguish mechanical style issues that tools can enforce from design issues requiring judgment.
6. Record findings with stable IDs, severity, evidence, impact, and the smallest corrective recommendation.
7. Set `decision` to `fix` only for material issues introduced by or blocking this task; use `needs-review` for unresolved architectural choices; otherwise approve and list non-blocking follow-ups.

## Cost and scope guardrails

- Do not redesign unaffected modules.
- Do not demand speculative extensibility, pattern adoption, or style migration.
- Do not duplicate findings already covered by the primary review; reference them when identifiable.
- A preference without repository policy or concrete impact is not a finding.
- If required evidence is unavailable, state the limitation instead of inferring quality.

## Output

Write the requested `review-maintainability*.md` artifact using the review front matter contract: `phase: "review"`, `decision: approve | fix | needs-review`, and stable `blocking_findings` when fixes are required. The orchestrator synthesizes this result with other review lanes before routing.
