# Design references

These sources informed the harness. They are guidance, not runtime dependencies; 0xSDLC keeps only practices that remain model-neutral and proportionate to a lightweight local tool.

| Source | Applied principle |
| --- | --- |
| [Anthropic — Building effective agents](https://www.anthropic.com/engineering/building-effective-agents) | Start with simple composable workflows, route only where specialization helps, use grounded tool results, and cap autonomous loops. |
| [Anthropic — Harness design for long-running application development](https://www.anthropic.com/engineering/harness-design-long-running-apps) | Use structured handoffs for context resets; separate generator and evaluator; make evaluation criteria explicit. |
| [OpenAI — Model guidance](https://developers.openai.com/api/docs/guides/latest-model?model=gpt-5.5) | State outcome, success criteria, evidence, constraints, and stopping conditions; keep prompts small; use relevant validation; scale reasoning only when evaluation justifies it. |
| [Addy Osmani — How to write a good spec for AI agents](https://addyosmani.com/blog/good-spec/) | Start from a concise goal; make specs living artifacts; capture commands, tests, project structure, style, Git workflow, and boundaries; split large work into focused contexts. |
| [Thoughtworks — Spec-driven development](https://www.thoughtworks.com/en-us/insights/blog/agile-engineering-practices/spec-driven-development-unpacking-2025-new-engineering-practices) | Treat specifications as durable, evolving engineering artifacts that connect intent, implementation, and validation. |
| [AGENTS.md](https://agents.md/) | Keep project-specific setup, test commands, conventions, and boundaries in a predictable repository-level instruction file. |

## How to use references responsibly

- Prefer the repository's `AGENTS.md` and current task specification over generic web guidance.
- Do not copy provider-specific commands or product claims into a generic contract without checking current official documentation.
- Treat recommendations as hypotheses: add a workflow stage, model call, or prompt rule only if it improves an observable harness failure, quality measure, or cost profile.
- When a provider changes behavior, update its adapter documentation and validate the installation path; do not alter shared phase semantics to fit one provider.
