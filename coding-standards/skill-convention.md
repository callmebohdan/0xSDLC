# Skill and agent convention

Every skill/subagent contract must be self-explanatory enough for a fresh model session.

## Required sections

1. Mission and non-mission.
2. When to use the skill.
3. Inputs and required context.
4. Step-by-step procedure.
5. Decision rules and edge cases.
6. Always/ask/never guardrails.
7. Output artifact and status rules.
8. Completion checklist.

## Writing style

- Prefer concrete verbs and observable outcomes.
- Define terms before using them.
- Explain what to do when evidence is missing.
- Include at least one realistic example for complex behavior.
- Separate facts, assumptions, decisions, and risks.
- Avoid “use best judgment” without describing the boundary of that judgment.

## Token discipline

Detailed does not mean duplicated. Put universal rules in `support/conventions/`; put only phase-specific rules in the phase folder; load the minimum relevant sections at runtime.

## Change checklist

- [ ] Contract has all required sections.
- [ ] It names forbidden shortcuts and stop conditions.
- [ ] Its output has a matching template.
- [ ] Its examples do not encode secrets or provider-specific assumptions.
- [ ] Validation and a representative dry-run pass.
