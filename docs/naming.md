# Naming and compatibility

`0xSDLC` is the product name and the preferred spelling anywhere a person reads, types, or discusses the harness. The capitalized `SDLC` keeps the familiar acronym legible and prevents the hexadecimal-style `0x` prefix from visually merging into the name.

## Preferred user-facing names

| Surface | Preferred form |
| --- | --- |
| Product, headings, and prose | `0xSDLC` |
| Main Python command | `python scripts/0xSDLC.py ...` |
| Convenience command | `python scripts/0xSDLC-autopilot.py ...` |
| CLI program name and output | `0xSDLC` |
| Phase contract folders | `0xSDLC-design`, `0xSDLC-plan`, and other `0xSDLC-*` names |

Documentation should use `0xSDLC` unless it is reproducing an exact machine identifier, path, environment variable, or provider invocation.

## Intentional lowercase identifiers

Some identifiers remain lowercase because changing them would break compatibility or reduce portability:

| Identifier | Why it stays lowercase |
| --- | --- |
| `$0xsdlc-*`, `/0xsdlc-*`, and `support/integrations/portable-skills/0xsdlc-*` | Provider skill IDs are machine-facing slugs; lowercase is the most portable form across Codex, Claude Code, Cursor, filesystems, and future adapters. |
| `.agents/0xsdlc` | This is the established runtime and session location. Renaming it would split existing installations and task history, and case-only paths behave differently across operating systems. |
| `scripts/sdlc_core` | Python import identifiers cannot start with a digit and should remain conventional lowercase module names. |
| `0XSDLC_*` | Environment variables conventionally use uppercase ASCII with underscores. |
| `.0xsdlc.lock` and `https://0xsdlc.local/...` | Internal persisted identifiers remain stable so old sessions and schemas continue to work. |

The compatibility forms are implementation details, not alternative branding. New public text should not introduce additional casing variants such as `0xsdlc`, `0XSdlc`, or `0XSDLC`.

## Filename rule

Files may start with `0` when the host filesystem and execution method permit it, so `scripts/0xSDLC.py` is the canonical executable filename. Python modules that must be imported use names such as `sdlc_core` instead. When a provider requires a lowercase slug, use `0xsdlc-*` for the identifier and retain `0xSDLC` in its display name and description.
