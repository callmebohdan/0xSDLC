# Claude adapter

Use this file as the Claude-specific translation layer. The repository contracts remain authoritative; this file only explains how to invoke Claude safely.

## Invocation contract

Configure `0XSDLC_CLAUDE_COMMAND` with an argument-array-compatible command template. Supported placeholders are `{prompt_file}`, `{workspace}`, `{output_dir}`, and `{task_id}`.

Example shape:

```text
claude --print --prompt-file {prompt_file}
```

Use the actual syntax supported by the installed Claude CLI. Do not assume that a command shown in documentation exists in every version.

## Claude session rules

- Start a fresh execution for each phase unless a deliberate continuation is recorded.
- Use the prompt packet as the phase boundary and task artifacts as the durable handoff.
- Keep write permissions disabled for read-only phases.
- Require Claude to inspect before editing and to run the narrowest relevant checks after editing.
- Require the named artifact, status, evidence, assumptions, failures, and next action.

## Failure handling

If Claude exits non-zero, times out, refuses a tool action, or writes no valid artifact, preserve stdout/stderr and mark the phase failed or blocked. Diagnose provider syntax and environment problems separately from product failures.

## Safety notes

Do not put API keys in this file or command templates committed to the repository. Review any command that can access network, credentials, deployment systems, or destructive tools before enabling `--execute`.
