# Core Rules

## `SCHEMA.MISSING_FIELD`

- Intent: Required adapter field missing.
- Default severity: `error`
- Example: Missing `name` in markdown frontmatter.
- False positives: Rare for strict schemas.
- Remediation: Add required field.

## `SCHEMA.INVALID_TYPE`

- Intent: Field has wrong data type.
- Default severity: `error`
- Example: `refs: foo` instead of list.
- False positives: Possible when adapters evolve.
- Remediation: Use expected type.

## `SCHEMA.INVALID_ENUM`

- Intent: Value not in allowed enum.
- Default severity: `error`
- Example: unsupported kind.
- False positives: Possible in evolving specs.
- Remediation: Use documented enum value.

## `SCHEMA.UNKNOWN_FIELD`

- Intent: Catch typos/unsupported fields.
- Default severity: `warning`
- Example: `descripton` typo.
- False positives: Adapter lag.
- Remediation: Fix typo or update adapter.

## `GRAPH.MISSING_TARGET`

- Intent: Refs selector has no target.
- Default severity: `error`
- Example: refs name that does not exist.
- False positives: None when resources are complete.
- Remediation: Create target or fix selector.

## `GRAPH.AMBIGUOUS_TARGET`

- Intent: Selector resolves to multiple targets.
- Default severity: `error`
- Example: same name across kinds.
- False positives: Expected in under-specified refs.
- Remediation: Specify `kind` and/or `path`.

## `GRAPH.INVALID_TARGET_KIND`

- Intent: Selector kind mismatches resolved target.
- Default severity: `error`
- Example: refs kind=skill but target is hook.
- False positives: Low.
- Remediation: Align kind metadata.

## `GRAPH.CYCLE_DETECTED`

- Intent: Disallowed cycle in dependency edges.
- Default severity: `error`
- Example: A depends_on B and B depends_on A.
- False positives: Possible when cycle types are intended.
- Remediation: Break cycle or allow ref type in config.
