# Codex skill metadata

Portable provider-neutral skill contracts live in `support/skills/`. This directory contains Codex-specific presentation metadata layered onto those skills during installation. Keeping metadata separate prevents Codex UI fields or invocation syntax from becoming part of the shared 0xSDLC contract.

`scripts/install.py --force` installs the portable wrappers for Codex, Claude Code, Cursor, and `.agents/skills`, then adds each available `agents/openai.yaml` file only to the Codex copy. Filesystem placement is structurally testable; interactive discovery still requires a host restart/rescan and harmless invocation.
