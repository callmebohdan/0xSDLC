# Codex adapter

Use this file as the Codex-specific translation layer. The repository contracts remain authoritative; this file only explains how to invoke Codex safely.

## Invocation contract

Configure `0XSDLC_CODEX_COMMAND` with an argument-array-compatible command template. Supported placeholders are `{prompt_file}`, `{workspace}`, `{output_dir}`, and `{task_id}`.

Example shape:

```text
codex exec --file {prompt_file}
```

Use the actual syntax supported by the installed Codex CLI. Do not assume that a command shown in documentation exists in every version.

## Codex session rules

- Start a fresh execution for each phase unless a deliberate continuation is recorded.
- Give Codex the active prompt packet, not the entire task history.
- Keep write permissions disabled for read-only phases.
- For implementation and fix phases, scope the working directory to the repository and keep task artifacts available.
- Ask Codex to write the named artifact and report evidence, not just summarize what it intended to do.

## Failure handling

If Codex exits non-zero, times out, refuses a tool action, or writes no valid artifact, preserve stdout/stderr and mark the phase failed or blocked. Do not retry unchanged after a product failure. Check whether the failure is provider syntax, permission, environment, or implementation behavior before deciding the next step.

## Safety notes

Do not put API keys in this file or command templates committed to the repository. Review any command that can access network, credentials, deployment systems, or destructive tools before enabling `--execute`.
