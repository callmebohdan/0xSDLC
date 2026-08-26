# Codex skill wrappers

These small wrappers make the canonical 0xSDLC contracts callable from Codex chat. They intentionally contain routing only; detailed behavior stays in the installed contracts under `%USERPROFILE%\\.agents\\0xsdlc`.

Install them with `scripts\\install.py --force`. Invoke `$0xsdlc-autopilot` for autonomous routing, or `$0xsdlc-agent` and name the phase you want, such as design, plan, implement, fix, or verify.
