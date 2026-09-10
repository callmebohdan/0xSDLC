# Model adapters

Adapters keep provider details out of the 0xSDLC workflow. The source contracts are in `support/adapters/`; the installer can publish them to the user-level `.agents/0xsdlc` directory.

## Environment configuration

The runner reads a command template from:

- `0XSDLC_CODEX_COMMAND`
- `0XSDLC_CLAUDE_COMMAND`
- `0XSDLC_GENERIC_COMMAND`
- future provider names such as `0XSDLC_QWEN_COMMAND` or `0XSDLC_LLAMA_COMMAND`.

Supported placeholders:

| Placeholder | Meaning |
| --- | --- |
| `{prompt_file}` | generated instructions for the active phase |
| `{workspace}` | repository root |
| `{output_dir}` | `.agents/0xsdlc/sessions/<task-id>/` |
| `{task_id}` | stable task identifier |

Example:

```powershell
$env:0XSDLC_CODEX_COMMAND = 'codex exec --file {prompt_file}'
python scripts\0xSDLC.py autopilot "Implement the requested change" --model codex --execute
```

Use the syntax supported by the installed provider version. The examples are shapes, not guarantees about every CLI release.

## Adapter responsibilities

An adapter must:

1. start the selected provider with the prompt packet;
2. use a fresh context per phase unless continuation is intentional and recorded;
3. preserve the workspace and task artifact boundary;
4. return or write the required artifact;
5. preserve stdout, stderr, exit code, and failure status;
6. avoid leaking secrets or unrelated source data.

It must not change route decisions, skip approvals, weaken guardrails, or claim tests it did not run.

## Permission profiles

Use the narrowest profile that supports the phase:

| Phase | Default permission |
| --- | --- |
| Intake/specify/audit/design/plan | read-only plus task artifact writes |
| Implement/fix | workspace writes within assigned scope |
| Test | read plus temporary test output; no production data |
| Review/verify | read-only plus report writes |
| High-risk | explicit human approval before write or external action |

## Failure handling

Record provider startup errors, invalid flags, timeouts, refusal, missing artifacts, non-zero exit codes, and tool permission failures. Classify the failure before retrying. A provider error is not a product failure; a product failure is not fixed by changing adapters.

## Security

Do not commit API keys, personal access tokens, cookies, private prompts, or provider state. Use environment or approved secret storage. Before sending repository content to a remote model, check the data classification and redact sensitive values.
