# Harness evaluation and cost control

0xSDLC should earn every extra instruction, artifact, and model call. Evaluate it against representative tasks before calling it more autonomous or adding new phase agents.

## What to measure

| Measure | Evidence | Why it matters |
| --- | --- | --- |
| Spec fidelity | acceptance criteria traced to implementation and verification | catches feature drift before it becomes polished wrong code |
| Evidence integrity | claims linked to commands, paths, tests, or approvals | prevents confident but unverified completion |
| Route efficiency | phases and calls per task class | exposes ceremony that does not improve outcomes |
| Recovery | a fresh session can continue from task artifacts | proves that handoffs, not chat memory, carry state |
| Review yield | actionable findings found before verification | tells whether independent review changes outcomes |
| Fix-loop behavior | attempt count per stable finding and final disposition | detects repeated, unproductive retries |
| Provider portability | same packet produces valid artifacts under each adapter | prevents one provider's syntax from becoming the architecture |
| Engineering-profile precision | relevant language guidance is loaded without overriding project rules | improves maintainability without universal-style drift |
| Maintainability-review yield | focused lane finds a material issue not found by normal review | determines whether its two extra calls are justified |

## Evaluation set

Maintain a small, sanitized set of representative tasks: one local bug, one standard feature, one integration/architecture change, one high-risk change that must stop for approval, one failing-review repair, and one resume after interruption. Each case should state expected route, required artifacts, expected stop point, and a reproducible acceptance check.

The dependency-free baseline is encoded in `tests/scenarios/l3-readiness.json` and exercised by `tests/fake_adapter.py`. It covers completion, artifact-declared blocking, approval/resume, adapter crash, malformed output, review/fix/retest/rereview, interrupted execution, adaptive routing, telemetry, and missing-project-instruction bootstrap.

Run structural checks first, then the narrowest relevant task checks. A harness change is acceptable only when it preserves or improves the expected route and evidence while not adding unmeasured calls to ordinary tasks.

## Cost decisions

1. Start sequentially with the smallest route.
2. Add design only when a technical decision changes risk, compatibility, or implementation shape.
3. Add a human gate for high-impact side effects, not for routine local edits.
4. Use focused maintainability review for architecture/reuse risk only when it can change the decision; it adds two calls.
5. Use parallel audit/review only when a second general perspective could materially change a decision. Its two independent lanes plus synthesis add four calls; combining both options adds five calls because review lanes share synthesis.
6. Stop a fix loop when the same stable finding has consumed two attempts or the route has consumed four fixes. Escalate the decision, not the token budget.
7. Keep static contracts before dynamic task evidence in an adapter prompt where the provider supports prefix caching; measure actual savings rather than assuming them.

## Failure review

When an evaluation fails, classify it before changing prompts: `specification`, `routing`, `tool/adapter`, `environment`, `implementation`, `test`, `review`, or `verification`. Fix the smallest layer that explains the failure, add a regression case, and avoid adding broad instructions that punish unrelated tasks.
