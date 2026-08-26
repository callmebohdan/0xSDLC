# Model adapters

This folder contains provider-specific translation contracts. The shared 0xSDLC phase contracts remain authoritative.

| Adapter | Configuration | Contract |
| --- | --- | --- |
| Claude | `0XSDLC_CLAUDE_COMMAND` | `claude.md` |
| Codex | `0XSDLC_CODEX_COMMAND` | `codex.md` |
| Cursor/generic CLI | `0XSDLC_GENERIC_COMMAND` or provider-specific wrapper | `cursor.md` |

Future Qwen, Llama, or other providers should add a small adapter contract and command mapping without copying the phase logic.
