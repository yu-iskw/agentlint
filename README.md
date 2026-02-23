# agentlint

`agentlint` is a static linter for coding-agent resources across Claude, Cursor, Gemini, and Codex.

## Install

```bash
uv sync --all-extras
```

## Quick Start

```bash
uv run agentlint init
uv run agentlint check --format human
```

## Commands

- `agentlint check`
- `agentlint explain RULE_ID`
- `agentlint dump-resources`
- `agentlint init`

## Config

Use `.agentlint.yaml` at repository root. See `docs/config-schema.md`.

Codex agent skills live in `.agents/skills` and are available when running Codex from this repo; use `.codex/config.toml` to disable specific skills if needed.

## CI

- Pre-commit hook metadata: `.pre-commit-hooks.yaml`
- GitHub Actions workflow: `.github/workflows/agentlint.yml`
