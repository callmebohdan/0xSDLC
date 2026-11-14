# Portable agent-skill integration

These wrappers follow the portable `SKILL.md` convention and make the canonical 0xSDLC contracts callable from hosts that support agent skills. They are intentionally provider-neutral. A host may expose them as `$0xsdlc-*`, `/0xsdlc-*`, an automatically selected skill, or another native action.

The wrappers intentionally contain routing only. Detailed behavior stays in the installed, model-neutral contracts under `0XSDLC_AGENTS_HOME` or the default user-level `.agents/0xsdlc` directory. This shared runtime location is separate from the current project's `AGENTS.md` instructions and its `.agents/0xSDLC/sessions/` task artifacts.

Before acting, read the project root `AGENTS.md` and the nearest nested instruction files that apply to the work. If root guidance is missing or inadequate, use the `init` readiness flow to prepare a reviewable draft; never create or update project rules silently.

The installer registers these skills in the native user-level skill directories supported by the selected tools. Invoke the autopilot skill for autonomous routing, or the phase-agent skill and name the phase you want, such as design, plan, implement, fix, or verify.
