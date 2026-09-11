# Maintainability contract

## Objective

Make the requested change easy to understand, test, operate, and modify without adding speculative machinery. Maintainability is not maximum abstraction, minimum line count, or conformity to a fashionable architecture; it is the expected cost and risk of correct future changes.

## Required reasoning

For each changed responsibility, establish:

- a clear owner and location;
- an explicit interface or data contract;
- dependencies flowing through existing boundaries;
- visible error, lifetime, state, and concurrency behavior;
- focused tests at the cheapest layer that proves behavior;
- operational evidence for failures that cannot be diagnosed from return values alone.

Prefer cohesive modules with narrow interfaces. Keep policy separate from I/O and provider details when that separation already exists or creates an immediate testing seam. Encapsulate volatile dependencies, but do not wrap stable code merely to create layers.

## Change rules

- Follow repository naming, layout, error, logging, testing, and dependency conventions.
- Optimize for readers and maintainers. Make ownership, units, state transitions, and surprising behavior explicit.
- Prefer standard-library and existing project facilities before adding dependencies or parallel abstractions.
- Remove duplication when the duplicated concept is stable and changes together. Allow small duplication when the abstraction would couple unrelated behavior or is not yet understood.
- Keep public surface area minimal. Do not expose implementation details for test convenience.
- Preserve compatibility unless the approved spec changes it. Treat API, ABI, schema, file-format, and persisted-state changes as explicit contracts.
- Keep a change locally reversible. Separate migrations, generated output, mechanical formatting, and behavior changes where practical.

## Maintainability risks

Report concrete evidence rather than labels. Typical risks include:

- one module knowing unrelated business, storage, transport, and presentation details;
- hidden global state, ambient configuration, or time-dependent behavior;
- ownership or cleanup that depends on every exit path being remembered;
- boolean flags or primitive parameters whose meaning is unclear at the call site;
- cyclic dependencies, inward dependencies on adapters, or cross-layer shortcuts;
- copy-pasted policy that can diverge;
- abstractions with no current consumer or meaningful substitution;
- tests coupled to private implementation rather than observable behavior;
- swallowed errors, unbounded retries, nondeterministic sleeps, or missing cancellation;
- comments that compensate for unclear code but are not checked against behavior.

## Evidence

A maintainability claim should cite at least one of: a repository convention, a reduced dependency edge, an explicit interface, a focused test seam, a static-analysis result, a measurable complexity/build/runtime effect, or a documented tradeoff. “Clean,” “SOLID,” “scalable,” and “best practice” are not evidence by themselves.

## Scope guardrail

Do not broaden a feature or bug fix into a cleanup campaign. Fix maintainability defects in the current route only when they block the acceptance criteria, create material safety risk, or are directly introduced by the change. Record other improvements as follow-ups.
