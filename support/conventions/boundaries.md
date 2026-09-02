# Harness boundaries and guardrails

These rules apply to every provider, phase, model, and autopilot route. More restrictive repository rules win.

## Always do

- Read the brief, relevant contract, current spec, and project instructions before acting.
- Inspect before editing; use existing project commands and conventions.
- Keep changes scoped to the current task and record unrelated findings separately.
- Preserve user modifications and never reset the working tree as a shortcut.
- Run the narrowest meaningful checks after a change.
- Record commands, exit codes, files changed, assumptions, risks, and next action.
- Treat secrets, private data, production access, and external side effects as sensitive.
- Prefer reversible changes and small commits or task slices.
- Stop when evidence is insufficient.

## Ask before doing

- Adding, removing, or upgrading dependencies.
- Changing CI, release, deployment, infrastructure, authentication, billing, or production configuration.
- Changing a database schema, data migration, public API, file format, or backward-compatibility contract.
- Sending data to an external service or using a non-local model with sensitive source content.
- Deleting, renaming, or mass-editing files outside the assigned scope.
- Running long-lived services, destructive commands, privileged commands, or commands with unclear side effects.
- Accepting a security, privacy, reliability, performance, or data-loss risk.
- Committing, merging, tagging, publishing, or releasing changes.

## Never do

- Commit or expose secrets, credentials, private keys, access tokens, cookies, or personal data.
- Disable security controls, authentication, validation, logging, tests, or review gates to get green output.
- Delete or weaken a failing test without an explicit approved requirement change.
- Use `--force`, broad deletion, destructive database commands, or history rewriting as a default shortcut.
- Modify `.git/`, installed dependency directories, vendored code, generated files by hand, or external repositories unless explicitly in scope.
- Claim a test, review, deployment, or verification was performed when it was not.
- Treat model output, a screenshot, or a type-check as proof of all acceptance criteria.

## Data handling

Before sending context to a provider, minimize it to the current task. Remove credentials and redact sensitive values. If the provider is not approved for the repository's data classification, stop with `needs-review`.

## Scope-drift rule

When you find a nearby problem, classify it as:

1. required to complete the current acceptance criteria;
2. a safety blocker;
3. a separate follow-up;
4. an optional cleanup.

Only categories 1 and 2 may change the current scope automatically. Record categories 3 and 4 without implementing them.
