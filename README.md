# 0xSDLC

0xSDLC is a lightweight, model-neutral harness for reliable software changes with AI coding agents.

It turns an underspecified request into a sequence of inspectable decisions and evidence:

```text
request → specification → audit → design → plan → implementation → test → review → verification
```

When review finds a defect, the harness routes the task through a bounded recovery loop:

```text
review → fix → test → review
```

The goal is not to make an AI agent autonomous at any cost. The goal is to make AI-assisted engineering understandable, repeatable, recoverable, and safe enough to supervise.

## Why 0xSDLC exists

Coding models are good at producing code quickly, but speed alone does not guarantee that the change solves the right problem. Common failures include:

- requirements disappearing into chat history;
- implementation beginning before the behavior is defined;
- changes being made in the wrong files or at the wrong scope;
- tests proving only that code runs, not that the requested behavior is correct;
- reviewers seeing incomplete context;
- failures being patched repeatedly without a stopping rule;
- agents claiming success without durable evidence.

0xSDLC addresses these problems with small phase agents, explicit input/output contracts, durable Markdown artifacts, structured route state, human gates, and provider-neutral adapters.

## When to use it

Use 0xSDLC when a task benefits from traceability, independent checking, or a controlled handoff between AI sessions:

| Situation | Recommended route | Why |
| --- | --- | --- |
| Typo, isolated test, or obvious local correction | `audit → plan → implement → test → review → verify` | Keeps process proportional to risk |
| Feature, bug fix, refactor, or multi-file change | `specify → audit → design → plan → implement → test → review → verify` | Defines behavior before implementation |
| Security, authentication, secrets, migration, deletion, production, payment, privacy, or public API work | Standard route plus `approval` before implementation | Makes blast radius and human authorization explicit |

Do not use the harness to disguise an unclear product decision. If two interpretations could lead to materially different behavior, the specification or human gate should stop and expose that decision.

## What it provides

### Focused subagents

Each agent has one responsibility:

- `specify`: define observable behavior and acceptance criteria;
- `audit`: inspect the repository, constraints, and existing patterns;
- `design`: choose the smallest safe technical approach;
- `plan`: divide the work into verifiable implementation slices;
- `implement`: change one planned slice;
- `test`: run focused behavioral and regression checks;
- `review`: independently assess correctness, risk, and contract conformance;
- `fix`: resolve one review finding with evidence;
- `verify`: map every acceptance criterion to final proof.

Intake is intentionally folded into the generated brief and specification. Quality assurance remains an optional release, compliance, or regulated-work gate rather than a default phase.

### Durable handoffs

Every phase produces a named artifact such as `spec.md`, `audit.md`, `design.md`, `plan.md`, `implementation.md`, `test-report.md`, `review.md`, or `verification.md`. The artifacts preserve:

- the source request and scope;
- assumptions and unresolved decisions;
- acceptance criteria and invariants;
- changed files and commands;
- evidence, failures, limitations, and residual risks;
- the exact next action.

The next agent can continue from these files without replaying the entire conversation.

### Controlled autonomy

Autopilot selects a risk-based route, invokes configured model adapters, records phase transitions in `route.json`, validates artifact metadata, pauses at approval gates, and stops on missing proof or unsafe conditions. It does not silently approve production actions, secrets, destructive changes, or unresolved requirements.

Review findings can trigger `fix → test → review`, but recovery is bounded: each stable finding receives at most two attempts and a cycle receives at most four total attempts.

### Model neutrality

The core contracts do not depend on a vendor SDK. Codex, Claude, Cursor, Qwen, Llama, and future providers can use the same phase semantics and artifact schemas through provider-specific integration wrappers.

## AI maturity

0xSDLC is a strong L2 system with early L3 capabilities.

It already provides repeatable workflows, phase boundaries, structured artifacts, risk-based routing, approval gates, resumable routes, evidence checks, bounded recovery, and optional independent audit/review lanes.

It is not yet a full L3/L4 platform. Important future work includes measured token budgets, crash-safe concurrency, provider health and cancellation, policy-enforced tool permissions, stable finding deduplication, and stronger synthesis of parallel results.

## Repository layout

```text
0xSDLC/
├── 0xSDLC-{autopilot,design,fix,implement,plan,verify}/  regular agents
├── support/
│   ├── agents/                                           less-frequent agents
│   ├── conventions/                                      shared rules
│   ├── adapters/                                         provider invocation contracts
│   ├── integrations/                                     provider-specific wrappers
│   └── mcp/                                              optional tool integration boundary
├── templates/                                             artifact templates and skill tests
├── orchestrator/                                          manifest and route metadata
├── docs/operations/                                       operating procedures
├── docs/                                                  rationale and reference
└── scripts/                                               dependency-free Python tooling
```

`AGENTS.md` remains at the repository root as the project-level instruction file.

Source contracts are versioned in this repository. Provider integrations consume the published model-neutral contracts, while generated task state and evidence live outside the repository in a user-level agent session directory.

```text
%USERPROFILE%\\.agents\\0xsdlc\\sessions\\YYYY-MM-DD_short-description_XXXXXXXX\\
```

This keeps runtime artifacts, transcripts, and potentially sensitive task details out of Git.

## Install and use

Run the single rollout command from the repository root:

```powershell
python scripts\\install.py --force
```

This publishes the model-neutral 0xSDLC library to `%USERPROFILE%\\.agents\\0xsdlc` and registers the portable skill wrappers in the native user-level skill locations for Codex, Claude Code, Cursor, and compatible tools. It does not install provider CLIs or configure credentials.

The contract library is shared; the invocation surface is provider-specific:

| Tool | Native invocation surface | Current 0xSDLC integration | Where native wrappers live |
| --- | --- | --- | --- |
| Codex | `$0xsdlc-autopilot`, `$0xsdlc-agent` | Native wrappers installed by this rollout | `%USERPROFILE%\\.codex\\skills` |
| Claude Code | `/0xsdlc-autopilot`, `/0xsdlc-agent` | Portable wrappers installed by this rollout | `%USERPROFILE%\\.claude\\skills` |
| Cursor | `/0xsdlc-autopilot`, `/0xsdlc-agent` | Portable wrappers installed by this rollout | `%USERPROFILE%\\.cursor\\skills` or `%USERPROFILE%\\.agents\\skills` |
| Qwen, Llama, Kiwi, other tools | Tool-specific command, skill, slash command, or rules mechanism | Shared library or adapter, if the tool supports one | Provider-specific location |

`$` and `/` are not 0xSDLC commands by themselves. They are host syntax for invoking a wrapper that loads the canonical contracts from `%USERPROFILE%\\.agents\\0xsdlc`. Native discovery happens only after the wrapper is copied into the host’s skill directory. This installer performs that registration for Codex, Claude Code, Cursor, and the portable `%USERPROFILE%\\.agents\\skills` location.

### Codex chat

After the rollout is visible to Codex, invoke the installed skills with `$`:

```text
$0xsdlc-autopilot Add CSV export to the reports page
$0xsdlc-agent Design the approved CSV export task
```

Use `$0xsdlc-autopilot` for the complete bounded route. Use `$0xsdlc-agent` when you explicitly want one phase such as `specify`, `audit`, `design`, `plan`, `implement`, `fix`, `test`, `review`, or `verify`.

### Claude Code

Claude Code can use the same contracts through the CLI adapter:

```powershell
$env:0XSDLC_CLAUDE_COMMAND = 'claude --print --prompt-file {prompt_file}'
python scripts\\0xsdlc.py autopilot "Add CSV export to the reports page" --model claude --execute --full
```

After installation, invoke `/0xsdlc-autopilot` or `/0xsdlc-agent` in Claude Code. Claude Code discovers the portable `SKILL.md` wrappers from `%USERPROFILE%\\.claude\\skills`; the wrappers then load the canonical contracts from `%USERPROFILE%\\.agents\\0xsdlc`.

### Cursor

Cursor can use the generated prompt interactively or through a local bridge/CLI:

```powershell
$env:0XSDLC_CURSOR_COMMAND = '<your Cursor bridge> {prompt_file}'
python scripts\\0xsdlc.py autopilot "Add CSV export to the reports page" --model cursor --execute --full
```

After installation, invoke `/0xsdlc-autopilot` or `/0xsdlc-agent` in Cursor. Cursor discovers user-level skills from `%USERPROFILE%\\.cursor\\skills` and the compatible `%USERPROFILE%\\.agents\\skills` location. Project-local installations can use `.cursor/skills/` when a workflow should travel with a repository.

### Other providers

Qwen, Llama, Kiwi, and future providers use the same adapter boundary:

```powershell
$env:0XSDLC_QWEN_COMMAND = '<provider command> {prompt_file}'
python scripts\\0xsdlc.py autopilot "Describe the change" --model qwen --execute --full
```

Use the provider’s actual command syntax and keep credentials outside the repository. Every provider still receives the same phase contracts, route state, artifact schema, and safety rules.

### Local-only preparation

To create a route and prompt packet without calling a model:

```powershell
python scripts\\0xsdlc.py autopilot "Describe the change you want"
```

See [AI readiness](docs/ai-readiness.md), [architecture](docs/architecture.md), [Git integration](docs/integrations/git.md), and [the agent library](docs/agent-library.md) for details.

## References and influences

The 0xSDLC contract model, spec-driven workflow, agent boundaries, artifact handoffs, and harness design were informed by these references:

- [Addy Osmani — Good spec](https://addyosmani.com/blog/good-spec/)
- [Thoughtworks — Spec-driven development: unpacking a new wave of engineering practices](https://www.thoughtworks.com/en-us/insights/blog/agile-engineering-practices/spec-driven-development-unpacking-2025-new-engineering-practices)
- [Addy Osmani — How to write a good spec for AI agents](https://addyo.substack.com/p/how-to-write-a-good-spec-for-ai-agents)
- [BrainGrid — Spec-driven development](https://www.braingrid.ai/spec-driven-development)
- [Anthropic — Building effective agents](https://www.anthropic.com/engineering/building-effective-agents#building-blocks-workflows-and-agents)
- [Anthropic — Harness design for long-running apps](https://www.anthropic.com/engineering/harness-design-long-running-apps)
- [Anthropic — Claude Code cheatsheet](https://support.claude.com/en/articles/14553413-claude-code-cheatsheet)
- [agents.md — Repository instruction convention](https://agents.md/)
- [Cursor — Custom commands](https://docs.cursor.com/en/agent/chat/commands)
- [Cursor — Rules](https://docs.cursor.com/context/rules)
- [OpenAI Developers — Model guidance and Codex skill invocation](https://developers.openai.com/api/docs/guides/latest-model?model=gpt-5.5)
