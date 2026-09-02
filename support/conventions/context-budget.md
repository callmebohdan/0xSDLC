# Context and cost policy

0xSDLC optimizes for the smallest context that can support an honest decision. More text and more agents do not automatically improve reliability; they increase cost, distraction, and the chance of conflicting instructions.

## Loading tiers

| Tier | Load | Use |
| --- | --- | --- |
| Minimal | project rules, brief, active contract, active template | simple inspection, planning, or documentation work |
| Standard | minimal plus current spec, relevant prior artifacts, focused source/tests | normal implementation, testing, review, and verification |
| Extended | standard plus architecture, integration, migration, security, or operational evidence | high-risk or cross-system work only |

Never load every phase contract, the entire repository, or the complete session transcript by default. Read only the sections and files named by the active contract. Summarize large evidence sets into a durable artifact and link the source paths.

## Model-call policy

- One primary agent per phase is the default.
- Parallel audit/review lanes are opt-in and must state their expected confidence gain and extra calls.
- Do not call a second model to repeat a deterministic command, inspect the same unchanged file, or restate an existing artifact.
- Prefer a cheaper model for classification, summarization, and mechanical checks; reserve stronger models for design, implementation, difficult fixes, and final verification.
- A retry requires a changed cause, context, or provider condition and must be recorded.

## Compression rules

- Preserve acceptance criteria, constraints, decisions, findings, commands, exit codes, and unresolved risks exactly.
- Remove conversational filler, duplicated explanations, and hidden reasoning.
- Replace long logs with a short result plus the log path; retain the original when it is needed for auditability.
- Never summarize away a failure, approval condition, security concern, or negative test.

## Budget failure

If the required context does not fit, split the task, create a focused evidence summary, or ask for a narrower scope. Do not omit safety-critical inputs or silently switch to a weaker evidence standard.
