# Architecture contract

## Objective

Choose the smallest architecture that satisfies current requirements while keeping important future changes affordable. Scalability includes team comprehension, build and test time, operational load, data volume, concurrency, deployment, and change isolation—not only request throughput.

## Design sequence

1. Name the required behavior, quality attributes, constraints, and non-goals.
2. Map existing components, ownership, data/control flow, and extension seams.
3. Identify what is likely to vary during the stated planning horizon; do not invent hypothetical variation.
4. Define module boundaries and dependency direction. Business policy should not depend directly on replaceable transport, UI, storage, clock, or provider details unless the project intentionally uses that architecture.
5. Define interfaces, invariants, state transitions, error semantics, cancellation, idempotency, and resource ownership.
6. Evaluate compatibility, migration, rollout, rollback, observability, performance, concurrency, and security.
7. Select the least complex option that meets measurable needs and explain rejected alternatives.

## Boundary quality

A useful boundary has a cohesive responsibility, a small explicit contract, and evidence that callers should not know its internals. Avoid boundaries that only rename or forward every operation. Prefer composition over inheritance when behavior can be assembled without an “is-a” contract; use inheritance when substitutability is real and enforced.

For public or cross-module interfaces, record inputs, outputs, ownership, lifetime, errors, thread-safety, ordering, versioning, and compatibility. Keep invalid states difficult to represent where the language and project conventions support it.

## Scaling questions

Only analyze dimensions relevant to the task:

- What grows: requests, data, tenants, modules, contributors, platforms, or build targets?
- Where are contention, serialization, allocation, network, storage, and retry boundaries?
- Can work be bounded, cancelled, retried safely, and observed?
- Does state have one owner and a recovery strategy?
- Can components be tested without production infrastructure?
- Will this change increase rebuild scope, binary/API coupling, or deployment coordination?

Do not add queues, caches, plugins, distributed services, generic repositories, or asynchronous execution without a demonstrated requirement and failure model.

## Decision record

For a material choice, `design.md` must capture context, chosen option, alternatives, consequences, evidence, migration/rollback, and the condition that would justify revisiting it. A pattern name is not a decision rationale.

## Review checks

- Dependencies follow intended boundaries without cycles or hidden service locators.
- Interfaces expose intent and do not leak volatile implementation details.
- Success, partial failure, timeout, retry, cancellation, and shutdown behavior are defined where relevant.
- State, ownership, concurrency, and consistency are explicit.
- Tests can exercise policy independently at an appropriate layer.
- Complexity is proportional to current requirements and measured risks.
