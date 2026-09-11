# Engineering quality, code style, and design patterns

0xSDLC treats code quality as an evidence-backed part of audit, design, implementation, test, and review—not as a universal formatting opinion or a mandatory extra phase.

## Ownership model

| Layer | Owns | Example |
| --- | --- | --- |
| Task | required behavior and approved constraints | compatibility must be preserved; latency target |
| Project | exact enforceable engineering policy | C++20, `.clang-format`, selected clang-tidy checks, exception policy |
| Language profile | safe questions and provisional defaults | RAII, explicit ownership, self-contained headers |
| 0xSDLC core | maintainability process and evidence rules | justify abstractions; prefer deterministic checks; avoid scope drift |

Higher layers win. A generic profile cannot override repository configuration or established local code. If a project has no policy, bootstrap records detected evidence and unresolved decisions; adoption still requires human review.

## What normal autopilot does

- Audit discovers language, build, formatting, lint, static-analysis, sanitizer, testing, and architecture evidence.
- Design evaluates boundaries, interfaces, ownership, failure behavior, relevant scale, and pattern costs when design is applicable.
- Implementation follows project rules and loads only the relevant language supplement.
- Test prefers deterministic tool output and records compiler/configuration/platform limitations.
- Review evaluates maintainability only through project policy or concrete correctness, coupling, ownership, testability, performance, or operational impact.

The runner always creates `project-profile.json`, using a bounded scan that ignores common dependency, build, VCS, and runtime directories. It uses detected languages only to select supplements; detection never declares a project policy.

## Optional maintainability review

Use:

```text
python scripts\0xSDLC.py autopilot "Refactor the event pipeline" --execute --full --maintainability-review
```

This runs the normal review and a focused maintainability lane concurrently, then synthesizes them before verification or a fix loop. It adds two model calls: one review and one synthesis. Recommended uses include reusable libraries, architectural changes, public APIs/ABIs, concurrency, performance-sensitive code, and changes expected to support several near-term variants.

Do not use it for routine formatting, renames, or obvious local fixes. `--parallel-checks` remains the broader independent audit/review option. Combining both options runs three review lanes with one synthesis and adds five calls across the complete route.

## Design-pattern policy

Patterns are reusable vocabulary, not quality badges. A proposed pattern must identify the current problem, simpler alternative, added indirection/lifetime/debugging cost, current consumers, test seam, and removal condition. Without that evidence, direct code wins.

The harness does not reward a pattern count or prescribe SOLID mechanically. It rejects speculative interfaces, forwarding-only layers, hidden global ownership, inheritance without substitutability, and plugin architectures without an approved need.

## C++ profile

The C++ supplement covers interfaces and strong types, RAII and ownership, Rule of Zero/Five, errors, concurrency, headers, templates, inheritance, build/ABI impact, and deterministic tools. It does not select Google, LLVM, Chromium, Unreal, Qt, AUTOSAR, or another ecosystem for the project.

For a new C++ repository, choose and check in the actual policy—language standard, supported compilers, warning level, formatter, static analysis, sanitizer targets, test framework, error strategy, exceptions/RTTI, API/ABI promise, naming, and generated-code rules. For an existing repository, follow its evidence and keep unrelated reformatting out of the task.
