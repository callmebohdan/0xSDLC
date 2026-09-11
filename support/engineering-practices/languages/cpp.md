# C++ engineering profile

## Scope and authority

Use this profile for C++ source detected in the task workspace. The project's selected C++ standard, compiler support, `.clang-format`, `.clang-tidy`, CMake/Meson configuration, contribution guide, and established code take precedence. Google, LLVM, Chromium, Unreal, Qt, AUTOSAR, safety-critical, embedded, and other ecosystems make different valid choices; do not merge them into an invented hybrid style.

For an undocumented new project, propose a baseline for human review. For an existing project, preserve local style and avoid unrelated reformatting.

## Interfaces and types

- Express intent with strong domain types, `const`, scoped enums, value types, and narrow interfaces.
- State ownership, lifetime, nullability, borrowing, mutation, thread-safety, units, ranges, and error behavior at boundaries.
- Avoid ambiguous adjacent primitive parameters; use a struct or named type when call-site meaning is unclear.
- Keep headers self-contained and include what they use. Minimize public-header implementation detail and accidental transitive dependencies.
- Keep public APIs and ABI concerns separate. Use Pimpl or C-compatible boundaries only when stability requirements justify their cost.
- Prefer non-member functions for operations that do not require object invariants; do not create classes merely to group static functions.

## Ownership and resources

- Use RAII for memory, files, locks, sockets, registrations, and every acquire/release pair.
- Prefer values and automatic storage. Use `std::unique_ptr` for exclusive dynamic ownership and `std::shared_ptr` only for genuine shared lifetime.
- Raw pointers and references normally express non-owning access; follow stricter project annotations where present.
- Prefer the Rule of Zero. When a type owns a resource directly, define or delete copy/move operations consistently and test lifetime behavior.
- Avoid naked `new`/`delete`, manual cleanup on multiple exits, owning globals, and hidden lifetime extension.

## Errors, state, and concurrency

- Follow one project-wide error strategy at each boundary: exceptions, expected/result types, status objects, or disciplined error codes. Do not mix strategies casually.
- Preserve invariants during failure. Define whether operations are transactional, retryable, idempotent, partially applied, or destructive.
- Use immutable data where practical and synchronize shared mutable state explicitly.
- Prefer scoped locks and standard concurrency primitives. Document lock ordering, thread ownership, cancellation, shutdown, and callback/reentrancy behavior.
- Never use timing sleeps as synchronization when a deterministic condition is available.

## Templates, inheritance, and patterns

- Use templates when compile-time genericity provides concrete type-safety, performance, or reuse benefits. Consider diagnostics, build time, binary size, and public-header coupling.
- Prefer concepts or clear constraints when supported by the selected standard.
- Prefer composition to implementation inheritance. Use public inheritance only for substitutable “is-a” relationships; give polymorphic bases safe destruction semantics.
- Avoid singletons and global registries unless ownership, initialization, teardown, and test isolation are explicitly solved.
- Do not introduce factories, visitors, observers, or policy hierarchies without current forces that justify them.

## Source, build, and compatibility

- Use the project filename, include-order, namespace, naming, and header-guard conventions exactly.
- Keep platform-specific code localized. Do not rely on compiler extensions unless the supported toolchain contract allows them.
- Respect the configured C++ standard and minimum compiler versions. Do not adopt a newer feature because a generic guide recommends it.
- Consider incremental build cost, generated code, symbol visibility, ODR hazards, ABI, serialization, and persisted formats where relevant.
- Warnings must not be suppressed globally to land a change; narrowly justify unavoidable suppression.

## Deterministic checks

Discover project commands first. Depending on configuration, relevant evidence may include:

- configured compiler warnings, preferably with warnings-as-errors in controlled CI targets;
- `clang-format` or the repository formatter;
- selected `clang-tidy` checks rather than an unreviewed all-checks policy;
- unit/integration tests and CTest;
- AddressSanitizer, UndefinedBehaviorSanitizer, ThreadSanitizer, or platform equivalents where risk and environment justify them;
- static analysis, include analysis, fuzzing, benchmarks, and ABI checks when the task requires them.

Record exact command, compiler/configuration, exit code, sanitizer limitations, and untested platforms. Compilation alone does not prove behavior; a formatter does not prove design quality.

## Review checklist

- Interface intent, ownership, lifetime, nullability, and errors are explicit.
- No resource can leak across early return, exception, cancellation, or partial construction.
- Copy/move/destruction and callback lifetimes are coherent.
- Concurrency assumptions and shutdown behavior are testable.
- Headers, templates, and dependencies do not impose unnecessary rebuild or API coupling.
- New abstraction has current consumers and a simpler alternative was considered.
- Tests cover behavior, boundaries, failure, and regression risk at the appropriate layer.
