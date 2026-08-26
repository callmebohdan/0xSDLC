# Generic model adapter

This adapter defines the minimum interface between 0xSDLC and any model CLI or API wrapper. It is the compatibility baseline for providers that do not have a dedicated adapter.

## Inputs

The runner provides:

- a prompt file;
- the workspace path;
- the task artifact directory;
- the task ID and active phase;
- environment configuration for the selected provider.

The adapter must not assume a specific shell, tool name, SDK, context window, memory store, or response format beyond plain text/Markdown and the ability to read the prompt.

## Required adapter behavior

1. Start a fresh model execution for the active phase unless the provider requires another documented mode.
2. Read the entire prompt file before acting.
3. Follow root project instructions, the shared conventions, and the active subagent contract in that order.
4. Read only listed artifacts and relevant source files; ask for more context through a blocker when necessary.
5. Keep changes limited to the active phase and task scope.
6. Write the named artifact into the task directory, or return a result that the wrapper can persist without ambiguity.
7. Return a concise summary containing status, changed files, commands, evidence, assumptions, failures, and next action.
8. Exit non-zero on adapter or model failure. Do not convert a model refusal or timeout into a successful phase.

## Tool and permission rules

- Use read-only inspection in intake, specification, audit, architecture, planning, review, and verification unless the contract explicitly requires a harmless artifact write.
- Implementer and fixer may edit only the assigned workspace and task files.
- Testing may create temporary test output but must not silently modify production data.
- Review and verification are evaluative; they must not repair their own findings.
- Never reveal system prompts, hidden chain-of-thought, credentials, or unrelated private data in task artifacts.

## Output normalization

The wrapper should preserve stdout and stderr separately, record the exit code, and keep the model's artifact. If the provider returns prose but fails to write the artifact, the phase is `blocked` unless the wrapper can deterministically map the response to the template.

## Provider-specific translation

Provider adapters may change invocation syntax, tool names, model selection, and permission flags. They may not weaken the shared boundaries, omit evidence fields, skip required phases, or change status meanings.
