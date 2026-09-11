# Model adapters

This folder contains provider-specific translation contracts. The shared 0xSDLC phase contracts remain authoritative.

| Adapter | Configuration | Contract |
| --- | --- | --- |
| Claude | `0XSDLC_CLAUDE_COMMAND` | `claude.md` |
| Codex | `0XSDLC_CODEX_COMMAND` | `codex.md` |
| Cursor/generic CLI | `0XSDLC_GENERIC_COMMAND` or provider-specific wrapper | `cursor.md` |

The portable skill wrappers are published separately to native user-level skill directories. An adapter is still required for providers that do not support the shared `SKILL.md` convention or that need CLI execution through `scripts/0xSDLC.py`.

Future Qwen, Llama, or other providers should add a small adapter contract and command mapping without copying the phase logic.

## Capability profiles

Machine-readable profiles under `profiles/` declare command configuration, skill discovery locations, read-only controls, parallel execution, and optional usage sidecars. The runner validates the declaration before selecting a provider. A profile documents capability; it does not prove that a CLI is installed, authenticated, or interactively discoverable.

Provider conformance has two levels:

1. Structural: profile schema, required capabilities, portable prompt/artifact contract, and wrapper placement tests.
2. Live: installed CLI syntax, authentication, permissions, skill discovery after restart/rescan, and a harmless end-to-end task.

Only structural conformance is suitable for automatic repository tests. Live conformance must run on the target machine and record its date and provider version.
