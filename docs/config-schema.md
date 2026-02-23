# `.agentlint.yaml` Schema (v1)

```yaml
version: 1
tools:
  claude:
    enabled: true
    roots: [".claude"]
    include: ["**/SKILL.md", "**/*.md"]
    exclude: []
validation:
  graph:
    allow_cycles: false
    cycle_ref_types_allowed: ["uses", "invokes"]
  cross_tool_refs: false
  rulesets: ["core"]
severities:
  SCHEMA.UNKNOWN_FIELD: warning
output:
  formats: ["human"]
  sarif:
    enabled: false
limits:
  max_file_size_kb: 2048
  follow_symlinks: false
```

Top-level keys:

- `version`
- `tools`
- `validation`
- `severities`
- `output`
- `limits`
