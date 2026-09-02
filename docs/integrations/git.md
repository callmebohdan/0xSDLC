# Git and pull-request integration

0xSDLC can prepare Git and pull-request handoffs, but Git hosting is an optional integration rather than a required phase. The harness remains useful for local work, repositories without a remote, and providers other than GitHub.

## Why keep Git separate

Source control contains durable collaboration state and may cause external side effects. A code change can be implemented and verified locally without pushing it, opening a pull request, merging it, changing branch protection, or releasing it. Separating these actions keeps the SDLC route model-neutral and prevents a model from treating a successful local test as permission to change shared remote state.

## What the agent may prepare

With the task’s scope and project rules, an agent may prepare:

- a descriptive branch name;
- a coherent commit plan and commit message;
- a pull-request title and description;
- changed-file and validation summaries;
- risk, rollback, approval, and reviewer-focus notes;
- links or paths to safe task artifacts.

Use [`templates/pull-request.md`](../../templates/pull-request.md) for the durable proposal and [`support/conventions/version-control.md`](../../support/conventions/version-control.md) for action boundaries.

## What requires explicit authorization

The user must explicitly authorize the exact external operation before the agent:

- pushes commits or tags;
- opens, edits, approves, merges, or closes a pull request;
- changes remote branches, branch protection, CI, releases, or deployments;
- force-pushes, rewrites shared history, or deletes remote refs.

“Create a PR” is authorization for creating that PR, but not for unrelated cleanup, force-pushing, merging, releasing, or modifying repository settings. The agent should confirm the target branch and exact scope before acting when they are not unambiguous.

## Evidence requirements

The handoff must distinguish:

- what was changed locally;
- what commands actually ran and their exit results;
- what review and verification established;
- what remains unperformed;
- whether a remote operation was requested, attempted, and confirmed.

Do not claim that a branch was pushed or a PR was created based on a generated URL, a CLI intent message, or a model response alone. Preserve the confirmed remote identifier and timestamp when available. If the result is uncertain, mark the handoff `needs-review`.

## Safe PR content

A useful PR description answers:

1. Why is the change needed?
2. What behavior or architecture changed?
3. What is out of scope?
4. How was it tested and verified?
5. What risks, migrations, approvals, or rollback steps matter?
6. What should the reviewer inspect closely?

Keep secrets, credentials, private task transcripts, hidden reasoning, and unredacted personal data out of commits and PR text.

## Recommended handoff sequence

```text
inspect status/diff
    ↓
run relevant checks
    ↓
complete review and verification artifacts
    ↓
prepare pull-request proposal
    ↓
human authorizes remote action
    ↓
perform and confirm the exact Git operation
```

The Git handoff complements verification; it does not replace tests, review, or proof of acceptance criteria.
