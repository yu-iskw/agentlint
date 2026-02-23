from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import yaml  # type: ignore[import-untyped]

from agentlint.models import Span


class FrontmatterError(Exception):
    """Raised when markdown frontmatter parsing fails."""


@dataclass
class MarkdownDocument:
    frontmatter: dict[str, Any] = field(default_factory=dict)
    body: str = ""
    locations: dict[str, Span] = field(default_factory=dict)


def parse_markdown(raw: str) -> MarkdownDocument:
    if not raw.startswith("---\n"):
        return MarkdownDocument(frontmatter={}, body=raw, locations={})

    lines = raw.splitlines(keepends=True)
    close_idx = None
    for idx in range(1, len(lines)):
        if lines[idx].strip() == "---":
            close_idx = idx
            break
    if close_idx is None:
        raise FrontmatterError("Unclosed YAML frontmatter block")

    frontmatter_block = "".join(lines[1:close_idx])
    try:
        frontmatter = yaml.safe_load(frontmatter_block) or {}
    except yaml.YAMLError as exc:
        raise FrontmatterError(f"Invalid frontmatter YAML: {exc}") from exc
    if not isinstance(frontmatter, dict):
        raise FrontmatterError("Frontmatter must be a YAML object")

    locations: dict[str, Span] = {}
    for line_no, line in enumerate(lines[1:close_idx], start=2):
        if ":" not in line:
            continue
        key = line.split(":", 1)[0].strip()
        if not key or key.startswith("#"):
            continue
        locations[key] = Span(
            line_start=line_no, col_start=1, line_end=line_no, col_end=max(1, len(line))
        )

    body = "".join(lines[close_idx + 1 :])
    return MarkdownDocument(frontmatter=frontmatter, body=body, locations=locations)
