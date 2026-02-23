# Security-lite Rules

## `SEC.POSSIBLE_SECRET_IN_METADATA`

- Intent: Flag potential inline secrets in metadata/frontmatter.
- Default severity: `warning`
- Example: `api_key: sk_live_...` in resource file.
- False positives: Tokens in examples/docs.
- Remediation: Move values to secret store and reference securely.

## `SEC.OVERBROAD_TOOL_PERMISSION`

- Intent: Detect wildcard/all tool grants.
- Default severity: `warning`
- Example: `tool_permissions: "*"`.
- False positives: Sandbox-only test environments.
- Remediation: Limit permissions to explicit set.

## `SEC.HOOK_OUTPUT_CONTRACT`

- Intent: Warn when hook output format is not JSON.
- Default severity: `warning`
- Example: `output_format: text` where JSON contract is expected.
- False positives: Adapters that accept plain text.
- Remediation: Set `output_format: json` where required.
