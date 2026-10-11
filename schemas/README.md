# Runtime schemas

`route.schema.json` defines the current machine-readable task state. `artifact.schema.json` defines the metadata at the top of every Markdown handoff. The Python runner performs the required dependency-free subset of these checks; external tooling may use a full JSON Schema validator.

Route schema `0.5` is current. It adds explicit task intent (`change`, `diagnose`, or `assessment`) and the opt-in quality-control route flag. The JSON Schema and dependency-free runtime validator both reject read-only routes containing `implement`, `fix`, or `approval`. The runner migrates `0.2`–`0.4` routes in memory, writes an explicit `route-migrated` event, and preserves `route.json.bak` before saving the migrated form. Artifact schemas `0.1` and `0.2` are accepted so existing sessions remain readable. Unknown versions stop with a clear error rather than being guessed into compatibility.

Migration to `0.5` supplies `mode: "change"` and `routing.quality_control: false` for old routes. Within a current schema, optional routing fields are normalized explicitly and recorded as route events.

Schema changes must include migration behavior, regression tests, and release notes. Never rewrite old task artifacts solely to make them appear current.
