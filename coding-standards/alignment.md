# Harness alignment standard

0xSDLC is aligned when the repository structure, agent contracts, runtime paths, and generated artifacts agree on the same source of truth.

## Required alignment

- Root `AGENTS.md` defines project-wide behavior and boundaries.
- Root `0xSDLC-*` folders contain the phase/subagent contracts.
- `support/adapters/` contains provider translation contracts only.
- `templates/` contains artifact schemas and agent-skill test templates.
- `support/0xSDLC-conventions/` contains shared rules used by every phase.
- `run-instructions/` contains how to load and execute agents.
- `orchestrator/` contains route/manifest and orchestration design.
- `scripts/` contains dependency-free implementation utilities.
- User-level `%USERPROFILE%\\.agents\\0xsdlc\\sessions` contains generated task state, reports, prompts, and transcripts.

## Naming rules

- Use `0xSDLC-<phase>` for root phase folders.
- Use domain names for phase contracts: `autopilot.md`, `planning.md`, `implementation.md`, `verification.md`, `audit.md`, and similar.
- Avoid generic filenames such as `Instructions.md` when the document has a specific domain.
- Keep provider names in `support/adapters/` and avoid provider assumptions in phase contracts.
- Never put generated task output beside source contracts.

## Review checklist

- [ ] New phase behavior has a root `0xSDLC-*` contract.
- [ ] New output has a template and validation rule.
- [ ] New provider behavior is isolated in `support/adapters/`.
- [ ] Python paths use the root-relative structure, not legacy paths.
- [ ] Global publishing includes only intended instruction assets.
