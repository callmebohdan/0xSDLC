# Portable agent-skill integration

These wrappers follow the portable `SKILL.md` convention and make the canonical 0xSDLC contracts callable from hosts that support agent skills. They are intentionally provider-neutral. A host may expose them as `$0xsdlc-*`, `/0xsdlc-*`, an automatically selected skill, or another native action.

The wrappers intentionally contain routing only. Detailed behavior stays in the installed, model-neutral contracts under the user-level `.agents/0xsdlc` directory.

The installer registers these skills in the native user-level skill directories supported by the selected tools. Invoke the autopilot skill for autonomous routing, or the phase-agent skill and name the phase you want, such as design, plan, implement, fix, or verify.
