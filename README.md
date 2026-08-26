# 0xSDLC

Spec-driven development harness for coding agents.

0xSDLC turns a short task into a durable, inspectable engineering loop:

`brief → spec → plan → tasks → implement → test → review → verify → fix`

It is intentionally model-neutral. Claude, Codex, Gemini, Qwen, Llama, or a future provider can use the same agent contracts and artifact format. The first implementation is dependency-free Python and works on Windows, macOS, and Linux wherever Python 3.10+ is available.

## Quick start

```text
python scripts\0xsdlc.py autopilot "Add CSV export to the reports page"
python scripts\0xSDLC-autopilot.py "Add CSV export to the reports page" --model codex --execute --full
python scripts\0xsdlc.py status
python scripts\validate_harness.py
```

The first command creates a task packet and chooses a route without calling an AI provider. Add `--execute` after configuring an adapter to let the selected CLI run. This separation makes the harness useful in a new repository, CI, or a manually supervised workflow.

## What is included

- `0xSDLC-autopilot/`, `0xSDLC-design/`, `0xSDLC-plan/`, `0xSDLC-implement/`, `0xSDLC-fix/`, and `0xSDLC-verify/`: frequently invoked agents.
- `support/`: less-frequent phase agents, shared conventions, adapters, and MCP boundaries.
- `support/adapters/`: Claude, Codex, Cursor, generic, and future provider translation contracts.
- `templates/`: artifact templates and agent-skill conformance tests.
- `coding-standards/`: alignment, pipeline, local-install, and skill conventions.
- `support/0xSDLC-conventions/`: shared phase protocol, evidence, status, and safety rules.
- `support/mcp/`: future MCP tool integration boundary.
- `orchestrator/`: manifest and orchestration design.
- `run-instructions/`: loading order and autopilot instructions.
- `scripts/0xsdlc.py`: dependency-free cross-platform orchestrator for task creation, route selection, prompt packets, adapter execution, and status.
- `scripts/validate_harness.py`: structural validation for the harness itself.
- User-level `.agents/0xsdlc/sessions/`: generated task artifacts and adapter transcripts, kept outside the repository.
- `AGENTS.md`: project-level rules that every supported model should read first.

The repository keeps source contracts in the root agents, `support/`, `templates/`, and documentation folders. Run `python scripts\install.py` to publish a copy to the user-level system directory `%USERPROFILE%\\.agents\\0xsdlc` on Windows or `~/.agents/0xsdlc` on macOS/Linux. Set `0XSDLC_AGENTS_HOME` to override that location.

## Adapter configuration

Adapters are configured with environment variables so the repository does not depend on a vendor SDK:

```text
0XSDLC_CODEX_COMMAND=codex exec --file {prompt_file}
0XSDLC_CLAUDE_COMMAND=claude --print --prompt-file {prompt_file}
```

The command template may use `{prompt_file}`, `{workspace}`, `{output_dir}`, and `{task_id}`. Use `--execute` only when the CLI is installed and you are comfortable with its permissions. The adapter receives the generated prompt packet; it does not receive hidden orchestration state.

## Design principles

1. Specs are the source of truth, not chat history.
2. Every phase has one job, one input contract, and one output artifact.
3. Context is selected by task slice; agents do not receive the entire repository by default.
4. Verification is independent from implementation where practical.
5. High-impact actions pause for approval; secrets and destructive shortcuts are hard stops.
6. Start with the simplest route and add parallel agents only when the task justifies the coordination cost.

See [`docs/agent-library.md`](docs/agent-library.md), [`run-instructions/autopilot.md`](run-instructions/autopilot.md), and [`support/0xSDLC-conventions/boundaries.md`](support/0xSDLC-conventions/boundaries.md) for the operating model.

## Autopilot modes

`autopilot` without `--execute` is a safe preparation mode. Add `--execute --full` to run the complete classified route. It stops at human approval gates, adapter failures, or missing required artifacts and records evidence under `.agents/0xsdlc/sessions/YYYY-MM-DD_short-description_XXXXXXXX/`.
