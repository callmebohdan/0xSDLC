# MCP integration boundary

MCP support is an extension point, not a required dependency of the core harness.

## Rules for future MCP servers

- Define each tool's inputs, outputs, side effects, permissions, and failure modes.
- Keep read-only and write-capable tools separate.
- Give tools narrow names and schemas; do not expose a generic unrestricted shell by default.
- Record external calls in the task artifact without storing secrets.
- Require approval for production, destructive, financial, privacy-sensitive, or irreversible tools.
- Provide deterministic mocks or fixtures for tests.

The base harness must remain usable without MCP installed.
