# Human interaction and autonomy

L3 changes how often the user steers execution, not who owns consequential decisions. Routine, reversible work may run through several phases in the background; the user receives progress and evidence rather than approving every transition. The harness pauses when human judgment or additional authority is required.

## Interaction modes

| Mode | User experience | Use case |
| --- | --- | --- |
| Prepare | packet and route are created; no provider executes | inspect scope and cost before starting |
| Standard autopilot | phases continue until completion, failure, or gate | ordinary local engineering work |
| Gated autopilot | planning completes, then implementation waits | sensitive, expensive, irreversible, or ambiguous work |
| Manual phase | user invokes one named agent | focused design, plan, review, fix, or verification |

## When a human acts

- Requirements conflict or a product choice materially changes the result.
- A configured or dynamically inserted approval gate is reached.
- Work needs dependencies, public API changes, migration, CI/release changes, secrets, production access, destructive operations, or external side effects.
- A fix budget is exhausted, review evidence is ambiguous, or a required environment is unavailable.
- Residual security, privacy, reliability, performance, or data-loss risk needs acceptance.

At a gate, show proposed scope, reason, risks, changes, validation plan, rollback, and estimated extra calls. Approval is explicit and durable. Resume records it in `approval.md` and `route.json`; silence is not approval.

## Background behavior

“Background” means eligible local phases may continue without another prompt. It does not grant new permissions. Hosts may run synchronously, in a background task, or across sessions; all forms use the same route and artifacts. After a process interruption, resume records recovery and retries the affected phase.

## Missing project instructions

Autopilot does not block merely because `AGENTS.md` is absent. It creates task-local `project-profile.json` and `project-context.md`. For recurring work, run `python scripts\0xSDLC.py bootstrap`, review `agents-draft.md`, and adopt that exact artifact with `python scripts\0xSDLC.py bootstrap --adopt TASK_ID --approve "decision"`. Existing `AGENTS.md` is never overwritten automatically.
