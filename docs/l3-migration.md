# L2 to L3 migration

0xSDLC can adopt L3 behavior incrementally. Phase contracts and the repository layout remain stable; maturity comes from better state, adaptation, recovery, evaluation, and provider execution—not from adding phases.

## Implemented foundations

| Foundation | Current behavior | L3 extension point |
| --- | --- | --- |
| Modular runner | canonical `scripts/0xSDLC.py` delegates to `scripts/sdlc_core/` | policies evolve behind one stable command |
| Schemas | route `0.4`, artifact `0.2`, and route `0.2`/`0.3` migration | add explicit migration fixtures for each release |
| Recovery | atomic writes, route backup, task lock, interrupted-phase recovery | leases for remote or multi-host workers |
| Provider capabilities | generic, Codex, Claude, Cursor profiles and structural checks | live versioned conformance and capability-aware routing |
| Evaluation | deterministic fake adapter and failure scenarios | real-project quality/cost baselines |
| Telemetry | local latency/exit records and optional token/cost sidecars | measured budget policies and dashboards |
| Adaptive routing | audit/design/plan may add `design` or `approval` with a reason | richer invalidation and task-slice scheduling |
| Project bootstrap | evidence profile and reviewable `AGENTS.md` draft | optional model refinement checked against facts |
| Engineering profiles | bounded project scan, selective C++ guidance, optional synthesized maintainability review | evaluated language expansion and measured review-yield policy |

## What is not L3 yet

The runner does not autonomously choose models by measured quality/cost, schedule implementation workers, invalidate all downstream evidence after arbitrary source changes, or prove live provider discovery on every host. Add these only against evaluation failures and real usage data.

Empty placeholders are intentionally avoided. Every extension point above has an executable contract or test; future behavior can replace policy behind the same interface.

## Promotion criteria

Call the harness L3 only when representative real tasks demonstrate unattended continuation between gates, interruption recovery without state loss, adaptive routes that improve outcomes, bounded repair, provider substitution with equivalent artifacts, and recorded quality/cost/latency sufficient to compare policies.
