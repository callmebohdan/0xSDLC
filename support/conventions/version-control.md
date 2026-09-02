# Version-control convention

Git is the default evidence boundary for source changes, but version-control actions are not an automatic SDLC phase. Agents may inspect local history and prepare a branch, commit, or pull-request proposal when the task allows it. They must not push, open a remote pull request, merge, delete branches, or rewrite history unless the user explicitly authorizes that exact action.

## Branches

Use a short, descriptive branch name that identifies the task without including secrets, issue contents, or personal data. Follow the repository’s existing prefix convention when one exists. Do not create a branch over unrelated user changes; inspect `git status` first and record the starting state in the task artifact.

## Commits

Commits should represent one coherent, reviewable change. A useful commit message states the change in imperative form and avoids claiming tests or behavior that were not verified. Do not commit generated sessions, adapter transcripts, credentials, local settings, or unrelated formatting changes.

Before proposing a commit:

- inspect the complete diff and `git status`;
- check for secrets and accidental generated files;
- run the narrowest relevant validation;
- record commands and results in the implementation or verification artifact;
- confirm the diff matches the approved scope.

## Pull requests

A pull-request description is a durable review handoff. It should explain why the change exists, what changed, how it was validated, known limitations, risk, rollback, and any approval or migration requirements. Link artifacts or evidence paths when they are safe to share. Never include tokens, private data, hidden reasoning, or unverified claims.

Use `templates/pull-request.md` when a task needs a PR proposal. The template is an output aid, not permission to create a remote PR.

## External Git actions

Treat these as explicit user-authorized operations:

- pushing commits or tags;
- opening, editing, approving, or merging a pull request;
- changing branch protection, releases, CI settings, or deployment configuration;
- force-pushing or rewriting shared history;
- deleting remote branches or tags.

If authorization is absent, prepare the exact command or PR text and stop at the handoff. If a remote result cannot be confirmed, report `needs-review` rather than assuming success.
