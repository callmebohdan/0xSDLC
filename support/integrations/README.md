# Provider integrations

0xSDLC has one canonical contract library and provider-specific registration layers.

```text
support/integrations/
├── portable-skills/       shared SKILL.md wrappers
└── codex/metadata/        Codex-only display metadata
```

The portable wrappers point to the installed canonical library selected by `0XSDLC_AGENTS_HOME`, or by default `%USERPROFILE%\\.agents\\0xsdlc` on Windows and `~/.agents/0xsdlc` on Unix-like systems. The installer copies them to native user-level locations:

| Host | Native user-level skill location |
| --- | --- |
| Codex | `%USERPROFILE%\\.codex\\skills` or `$CODEX_HOME/skills` |
| Claude Code | `%USERPROFILE%\\.claude\\skills` or `$CLAUDE_CONFIG_DIR/skills` (installer honors `CLAUDE_CONFIG_DIR`) |
| Cursor | `%USERPROFILE%\\.cursor\\skills` or `%USERPROFILE%\\.agents\\skills` |

The host owns discovery and invocation syntax. Depending on the host, the same wrapper may be invoked with `$0xsdlc-autopilot`, `/0xsdlc-autopilot`, an automatically selected skill, or an explicit CLI command. The wrapper must not duplicate phase logic or change artifact semantics.

Provider-specific metadata, permissions, command syntax, and authentication remain outside the portable wrapper. Keep credentials out of this repository and out of generated artifacts.

## Shared instructions and project artifacts

The shared runtime library contains 0xSDLC contracts and tools. It is not a project-policy or session directory. In the active repository, read root `AGENTS.md` plus the nearest nested `AGENTS.md` files relevant to the files in scope. New task sessions go to `<project-root>/.agents/0xSDLC/sessions/<task-id>` unless `--sessions-root` or `0XSDLC_SESSIONS_ROOT` is set. To publish updated shared contracts and wrappers from this checkout, run `python scripts/install.py --upgrade`. Provider wrappers should reference these conventions, not duplicate phase rules.
