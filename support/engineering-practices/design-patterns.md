# Design-pattern selection contract

## Principle

Design patterns are names for recurring solution shapes. Use them to communicate a design that the problem already requires; never make “use a pattern” a requirement by itself. The simplest direct implementation is the baseline alternative.

## Selection test

Before introducing or extending a pattern, record:

1. the concrete recurring problem and forces;
2. the current evidence that direct code is insufficient;
3. the pattern's participants and the project concepts they represent;
4. simpler alternatives and why they fail a requirement;
5. added interfaces, indirection, allocations, lifetime rules, and debugging cost;
6. how substitutability and behavior will be tested;
7. the condition under which the abstraction should be simplified or removed.

If these answers are weak, do not introduce the pattern.

## Practical guidance

| Need | Possible shape | Prefer it when | Warning |
| --- | --- | --- | --- |
| Select interchangeable policy | Strategy or callable | behavior genuinely varies at runtime/build time and callers need one contract | one implementation or boolean branching may be clearer |
| Translate an external interface | Adapter | third-party/provider semantics must stay outside the core | do not mirror every dependency method mechanically |
| Construct a validated complex object | Builder or named factory | construction has meaningful invariants or alternatives | trivial constructors do not need ceremony |
| Notify independent consumers | Observer/event | fan-out and lifecycle semantics are explicit | subscriptions create ownership, ordering, and reentrancy risks |
| Encapsulate an operation | Command | queuing, undo, audit, or delayed execution is required | direct function calls are usually cheaper |
| Vary object creation | Factory | callers must be isolated from concrete selection | avoid global registries and stringly typed creation |
| Add behavior around a stable interface | Decorator | composition and ordering are meaningful | stacked wrappers can obscure control flow |
| Represent state-dependent behavior | State | transitions and allowed operations form a real state machine | an enum and switch may remain clearer |

Patterns not listed here are neither forbidden nor endorsed. Evaluate their forces and costs the same way.

## Anti-pattern guardrails

- Do not create an interface solely because testing tools can mock it.
- Do not use inheritance for code sharing without substitutability.
- Do not use Singleton or service locator to hide ownership and dependencies.
- Do not add repository/service/facade layers that only forward calls.
- Do not combine several patterns to anticipate unrequested plugins or providers.
- Do not call an existing local convention an anti-pattern without concrete failure evidence.

## Review outcome

A reviewer may request a fix when new indirection creates concrete correctness, ownership, testing, performance, or change-isolation risk. Personal preference for another pattern is at most a follow-up unless backed by project policy or measurable impact.
