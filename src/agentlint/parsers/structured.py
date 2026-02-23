from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import yaml  # type: ignore[import-untyped]


class ParseError(Exception):
    """Raised when structured parsing fails."""


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError as exc:
        raise ParseError(f"Non-UTF8 file: {path}") from exc


def parse_yaml(raw: str) -> dict[str, Any]:
    try:
        value = yaml.safe_load(raw)
    except yaml.YAMLError as exc:
        raise ParseError(f"YAML parse error: {exc}") from exc
    if value is None:
        return {}
    if not isinstance(value, dict):
        raise ParseError("YAML root must be an object")
    return value


def parse_json(raw: str) -> dict[str, Any]:
    try:
        value = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise ParseError(f"JSON parse error: {exc}") from exc
    if not isinstance(value, dict):
        raise ParseError("JSON root must be an object")
    return value
