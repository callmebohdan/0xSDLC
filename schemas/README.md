# Runtime schemas

`route.schema.json` defines the current machine-readable task state. `artifact.schema.json` defines the metadata at the top of every Markdown handoff. The Python runner performs the required dependency-free subset of these checks; external tooling may use a full JSON Schema validator.

Route schema `0.4` is current. The runner migrates `0.2` and `0.3` routes in memory, writes an explicit `route-migrated` event, and preserves `route.json.bak` before saving the migrated form. Artifact schemas `0.1` and `0.2` are accepted so existing sessions remain readable. Unknown major or minor versions stop with a clear error rather than being guessed into compatibility.

Backward-compatible optional state added within `0.4` is normalized explicitly. For example, routes created before focused maintainability review receive `routing.maintainability_review: false` and a `route-normalized` event when resumed.

Schema changes must include migration behavior, regression tests, and release notes. Never rewrite old task artifacts solely to make them appear current.
