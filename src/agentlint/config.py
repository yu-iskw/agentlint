from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml  # type: ignore[import-untyped]

from agentlint.models import Severity, ToolId

CONFIG_FILENAME = ".agentlint.yaml"


DEFAULT_CONFIG: dict[str, Any] = {
    "version": 1,
    "tools": {
        "claude": {
            "enabled": True,
            "roots": [".claude"],
            "include": ["**/SKILL.md", "**/*.md"],
            "exclude": [],
        },
        "cursor": {
            "enabled": True,
            "roots": [".cursor"],
            "include": ["**/*.md"],
            "exclude": [],
        },
        "gemini": {
            "enabled": True,
            "roots": [".gemini"],
            "include": ["**/*.json", "**/*.yaml", "**/*.yml", "**/*.md"],
            "exclude": [],
        },
        "codex": {
            "enabled": True,
            "roots": [".codex"],
            "include": ["**/*.md", "**/*.json", "**/*.yaml", "**/*.yml"],
            "exclude": [],
        },
    },
    "validation": {
        "graph": {
            "allow_cycles": False,
            "cycle_ref_types_allowed": ["uses", "invokes"],
        },
        "cross_tool_refs": False,
        "rulesets": ["core"],
    },
    "output": {
        "formats": ["human"],
        "sarif": {"enabled": False},
    },
    "limits": {
        "max_file_size_kb": 2048,
        "follow_symlinks": False,
    },
    "severities": {
        "SCHEMA.UNKNOWN_FIELD": Severity.WARNING.value,
        "SEC.POSSIBLE_SECRET_IN_METADATA": Severity.WARNING.value,
        "SEC.OVERBROAD_TOOL_PERMISSION": Severity.WARNING.value,
        "SEC.HOOK_OUTPUT_CONTRACT": Severity.WARNING.value,
    },
}


class ConfigError(Exception):
    """Raised when configuration is invalid."""


@dataclass(frozen=True)
class Config:
    raw: dict[str, Any]
    path: Path | None

    def severities(self) -> dict[str, Severity]:
        severities: dict[str, Severity] = {}
        for code, value in self.raw.get("severities", {}).items():
            severities[code] = Severity(value)
        return severities


def _deep_merge(base: dict[str, Any], override: dict[str, Any]) -> dict[str, Any]:
    result = deepcopy(base)
    for key, value in override.items():
        if isinstance(value, dict) and isinstance(result.get(key), dict):
            result[key] = _deep_merge(result[key], value)
        else:
            result[key] = value
    return result


def _validate_config(config: dict[str, Any]) -> None:
    if config.get("version") != 1:
        raise ConfigError("Only version: 1 is supported in .agentlint.yaml")
    for tool in config.get("tools", {}):
        if tool not in {item.value for item in ToolId if item != ToolId.UNKNOWN}:
            raise ConfigError(f"Unsupported tool in config: {tool}")


def load_config(cwd: Path, config_path: Path | None = None, ci: bool = False) -> Config:
    candidate = config_path or (cwd / CONFIG_FILENAME)
    raw = deepcopy(DEFAULT_CONFIG)

    if candidate.exists():
        try:
            loaded = yaml.safe_load(candidate.read_text(encoding="utf-8")) or {}
        except yaml.YAMLError as exc:
            raise ConfigError(f"Failed to parse {candidate}: {exc}") from exc
        if not isinstance(loaded, dict):
            raise ConfigError("Config must be a YAML object")
        raw = _deep_merge(raw, loaded)
        source_path: Path | None = candidate
    else:
        source_path = None

    if ci:
        claude_roots = raw.get("tools", {}).get("claude", {}).get("roots", [])
        raw["tools"]["claude"]["roots"] = [
            root for root in claude_roots if not root.startswith("~")
        ]

    _validate_config(raw)
    return Config(raw=raw, path=source_path)
