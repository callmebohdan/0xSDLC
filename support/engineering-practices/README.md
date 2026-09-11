# Engineering-practice supplements

These contracts help 0xSDLC produce code that remains understandable, changeable, testable, and operational as a project grows. They supplement—not replace—the task specification, repository `AGENTS.md`, checked-in formatter/linter configuration, build settings, and established local code.

## Precedence

Apply guidance in this order:

1. current task specification and approved design decisions;
2. repository and directory-level instructions;
3. executable project configuration and consistently established code conventions;
4. the applicable language profile in this directory;
5. generic maintainability, architecture, and pattern guidance.

When sources conflict, preserve the higher-priority rule and record the conflict. Do not silently restyle a repository to match a generic profile.

## Loading policy

The runner selects supplements by phase and detected language. It does not paste this whole library into every prompt:

| Context | Supplements |
| --- | --- |
| Design | architecture and design-pattern selection |
| Implementation/fix | maintainability |
| C++ design, implementation, test, or review | C++ profile |
| Optional maintainability review lane | all generic supplements plus applicable language profile |

Language detection is evidence, not authority. A profile supplies safe review questions and defaults for a new or undocumented project; it does not authorize a mass migration.

## Automation boundary

Prefer deterministic enforcement—formatters, compiler diagnostics, linters, static analysis, sanitizers, and tests—over asking a model to judge mechanically checkable rules. Models should interpret architecture, intent, tradeoffs, and gaps the tools cannot establish.
