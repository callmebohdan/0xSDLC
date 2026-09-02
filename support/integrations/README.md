# Provider integrations

0xSDLC has one canonical contract library and provider-specific registration layers.

```text
support/integrations/
├── portable-skills/       shared SKILL.md wrappers
└── codex/metadata/        Codex-only display metadata
```

The portable wrappers point to the installed canonical library under `%USERPROFILE%\\.agents\\0xsdlc` on Windows or `~/.agents/0xsdlc` on Unix-like systems. The installer copies them to native user-level locations:

| Host | Native user-level skill location |
| --- | --- |
| Codex | `%USERPROFILE%\\.codex\\skills` or `$CODEX_HOME/skills` |
| Claude Code | `%USERPROFILE%\\.claude\\skills` or `$CLAUDE_CONFIG_DIR/skills` |
| Cursor | `%USERPROFILE%\\.cursor\\skills` or `%USERPROFILE%\\.agents\\skills` |

The host owns discovery and invocation syntax. Depending on the host, the same wrapper may be invoked with `$0xsdlc-autopilot`, `/0xsdlc-autopilot`, an automatically selected skill, or an explicit CLI command. The wrapper must not duplicate phase logic or change artifact semantics.

Provider-specific metadata, permissions, command syntax, and authentication remain outside the portable wrapper. Keep credentials out of this repository and out of generated artifacts.
