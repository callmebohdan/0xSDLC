# MCP integration boundary

MCP is optional. The core harness must work with local files, Python, and provider adapters alone. Add MCP only when a narrow, well-described tool provides evidence or an action that the local environment cannot safely provide.

## When a tool is justified

Use MCP for a bounded capability such as reading approved issue data, querying a documented service, running a browser acceptance check, or creating a ticket after explicit approval. Do not add it merely to expose a generic shell, browser, filesystem, or production control plane.

## Tool contract

Every proposed tool needs versioned Markdown that states:

| Field | Required detail |
| --- | --- |
| Purpose | one job and the decision it supports |
| Inputs | schema, required values, validation, and redaction |
| Outputs | schema, examples, and which values are evidence |
| Permissions | read-only/write-capable, identity, and data scope |
| Side effects | external writes, cost, notifications, state changes, reversibility |
| Failure modes | timeouts, partial success, retry safety, rate limits, recovery |
| Audit trail | what a task artifact records without secrets |
| Test strategy | deterministic fixture/mock plus denial/error case |

Use explicit names such as `issue_get` or `browser_check_route`, not an overloaded `run` tool. Keep read-only and write-capable operations separate. Make dangerous parameters difficult to provide accidentally; the interface should prevent mistakes instead of relying on reminders.

## Autopilot policy

- Read-only tools may support audit, design, planning, testing, review, or verification when their data classification is approved.
- Write-capable tools are implementation actions. Production, financial, destructive, privacy-sensitive, irreversible, or notification-producing calls require explicit approval.
- Before an external call, minimize context and remove credentials, tokens, private keys, cookies, and unrelated source.
- Record tool name, sanitized inputs, timestamp, result summary, external ID, and limitations in the phase artifact. Never record secrets.
- A successful call proves only the fact observed or action performed; it does not prove an entire acceptance criterion.

## Provider portability

An MCP server is not part of a generic phase contract. Provider adapters document their discovery and permission mechanics; shared phase contracts describe required outcome and evidence. If a provider cannot use an approved server, use a documented local fallback or report `blocked`/`needs-review`.

## Before adding a server

1. Show why an existing command or fixture is insufficient.
2. Define least-privilege permissions and approval policy.
3. Add deterministic mocks and failure-mode tests.
4. Add a sanitized task-artifact example.
5. Validate real provider discovery and permissions; installation alone does not prove interactive availability.
