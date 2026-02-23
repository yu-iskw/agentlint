# Architecture

`agentlint` follows a static, adapter-driven pipeline:

1. Discovery (`discovery.py`)
2. Parsing (`parsers/`)
3. Normalization (adapters)
4. Validation (schema, graph, security-lite)
5. Reporting (`human`, `json`, `sarif`)

The core model is shared across all adapters:

- `Resource`
- `Reference`
- `Issue`

No repository code execution is performed by design.
