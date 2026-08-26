# Sessions and output

Runtime task state is stored outside the repository in the user-level agent directory: `%USERPROFILE%\\.agents\\0xsdlc\\sessions` on Windows, or `~/.agents/0xsdlc/sessions` on macOS/Linux.

## Layout

```text
~/.agents/0xsdlc/
└── sessions/
    └── YYYY-MM-DD_short-description_XXXXXXXX/
        ├── brief.md
        ├── route.json
        ├── prompt-<phase>.md
        ├── <phase reports>.md
        └── adapter stdout/stderr transcripts
```

Keep one task's evidence together. Never overwrite a failed report to make the task appear green. Redact secrets and private data from artifacts before sharing them. The eight-character suffix prevents collisions while keeping paths readable.
