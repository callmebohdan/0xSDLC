# 0xSDLC

0xSDLC is a lightweight, model-neutral harness for taking an engineering request from a clear specification to evidence-backed verification. It is for teams who want the discipline of spec-driven development without a framework, hosted control plane, or permanent swarm of agents.

The harness uses Markdown contracts and dependency-free Python. A task remains portable across Codex, Claude Code, Cursor, and future adapters because its source of truth is a small task packet and durable artifacts—not one provider's chat history.

## Why use it

- **Less drift:** `spec.md` captures behavior and acceptance criteria before implementation; code does not silently redefine the request.
- **Cheaper context:** each phase loads its own contract and only relevant evidence. Completed work is handed off through files, not a growing transcript.
- **Honest completion:** test, review, and final verification are distinct decisions. The runner stops on invalid artifacts, missing evidence, failing adapters, and approval gates.
- **Controlled autonomy:** autopilot chooses a minimal route, while sensitive work waits for an explicit human decision.
- **Provider freedom:** adapters change invocation syntax, not requirements, artifact schemas, or safeguards.

0xSDLC is not a project manager, autonomous release bot, or a replacement for code review. It is a repeatable engineering loop for a repository you already control.

## Operating model

```text
request → specify → audit → [design] → plan → [approval] → implement → test → review → verify
                                                        ↑                 │
                                                        └── fix ←─────────┘
```

`design` is conditional: autopilot includes it for high-risk or architecturally consequential work and can be overridden with `--with-design` or `--without-design`. `approval` is mandatory for high-risk routes and optional otherwise. Quality control is an optional release/compliance gate, not a default stage. A fix loop preserves every attempt, retests, rereviews, and stops after two attempts per stable finding or four attempts per route.

Small work still receives review: `audit → plan → implement → test → review → verify`. This avoids the false economy of omitting independent assessment while retaining a low-call route.

## Start here

Install the repository copy into the user-level runtime library and Codex, Claude Code, Cursor, and shared skill locations, then restart or rescan your AI tool:

```text
python scripts\install.py --force
```

Prepare a task without calling a provider:

```text
python scripts\0xSDLC-autopilot.py "Add CSV export to the reports page"
```

The command creates `%USERPROFILE%\.agents\0xsdlc\sessions\YYYY-MM-DD_short-description_8hex\`, containing `brief.md`, `route.json`, and the first prompt. This is runtime state outside Git; this repository contains the reusable contracts and templates.

To let a configured adapter execute the complete route:

```text
python scripts\0xSDLC-autopilot.py "Add CSV export to the reports page" --model codex --execute --full
```

Inspect sessions with `python scripts\0xSDLC.py status`. A route at an approval gate resumes only after the human records approved scope:

```text
python scripts\0xSDLC.py resume TASK_ID --approve "Implement the reviewed plan; no public API change" --execute --full
```

For a repository without project instructions, prepare a reviewable draft without changing the repository:

```text
python scripts\0xSDLC.py bootstrap --workspace C:\path\to\project
```

See [installation and provider use](docs/install.md), [workflow](docs/workflow.md), [architecture](docs/architecture.md), [human interaction](docs/human-interaction.md), [naming and compatibility](docs/naming.md), and [L3 migration](docs/l3-migration.md) for operating details.

## Cost policy

The sequential route is the normal route: one call per applicable phase. Do not add agents because they sound sophisticated. `--parallel-checks` adds an independent audit and review plus a synthesis after each pair, adding four model calls. Use it only for high uncertainty or high impact; two opinions without reconciliation are not meaningful validation.

Prompts should be outcome-first and small: static contracts first, current task evidence last; targeted checks before broad checks; and stop when criteria are proven or a meaningful blocker remains.

## Repository map

| Location | Purpose |
| --- | --- |
| `0xSDLC-*` | frequently invoked model-facing phase contracts |
| `support/` | less-frequent agents, shared guardrails, adapters, MCP boundary, and compatibility material |
| `templates/` | durable task-artifact schemas |
| `docs/` | human-facing architecture, operation, installation, and references |
| `scripts/` | cross-platform runner, installer, and structural validator |
| `orchestrator/` | compact manifest and integration boundary |
| `AGENTS.md` | project-specific instructions read before a phase starts |

## Design sources

0xSDLC uses the portable parts of guidance from Anthropic (start simple, bounded workflows, ground truth, structured handoffs, independent evaluation), OpenAI (outcome-first prompts, success/stop rules, targeted validation, measured escalation), and spec-driven-development practice (explicit requirements, commands, tests, repository conventions, Git rules, and boundaries). The full dated list is in [docs/references.md](docs/references.md).
