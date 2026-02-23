from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any


class ToolId(str, Enum):
    CLAUDE = "claude"
    CURSOR = "cursor"
    GEMINI = "gemini"
    CODEX = "codex"
    UNKNOWN = "unknown"


class ResourceKind(str, Enum):
    SKILL = "skill"
    SUBAGENT = "subagent"
    HOOK = "hook"
    PLUGIN = "plugin"
    RULE = "rule"
    CONFIG = "config"
    UNKNOWN = "unknown"


class ContentType(str, Enum):
    MARKDOWN = "markdown"
    YAML = "yaml"
    JSON = "json"
    TEXT = "text"


class RefType(str, Enum):
    USES = "uses"
    INVOKES = "invokes"
    INCLUDES = "includes"
    DEPENDS_ON = "depends_on"
    REGISTERS = "registers"
    EXTENDS = "extends"


class Severity(str, Enum):
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


@dataclass(frozen=True)
class Span:
    line_start: int
    col_start: int
    line_end: int
    col_end: int


@dataclass(frozen=True)
class ResourceSelector:
    tool: ToolId | None = None
    kind: ResourceKind | None = None
    name: str | None = None
    path: str | None = None


@dataclass(frozen=True)
class Reference:
    from_id: str
    to_selector: ResourceSelector
    ref_type: RefType
    confidence: float = 1.0
    source_span: Span | None = None
    raw: str = ""


@dataclass
class Resource:
    id: str
    tool: ToolId
    kind: ResourceKind
    name: str
    path: Path
    content_type: ContentType
    frontmatter: dict[str, Any] = field(default_factory=dict)
    body: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)
    refs: list[Reference] = field(default_factory=list)
    locations: dict[str, Span] = field(default_factory=dict)


@dataclass
class Issue:
    """A normalized lint finding emitted by validators."""

    severity: Severity
    code: str
    message: str
    path: Path
    span: Span | None = None
    tool: ToolId | None = None
    kind: ResourceKind | None = None
    suggestion: str | None = None
    documentation: str | None = None

    def to_dict(self) -> dict[str, Any]:
        data: dict[str, Any] = {
            "severity": self.severity.value,
            "code": self.code,
            "message": self.message,
            "path": str(self.path),
        }
        if self.span:
            data["span"] = {
                "line_start": self.span.line_start,
                "col_start": self.span.col_start,
                "line_end": self.span.line_end,
                "col_end": self.span.col_end,
            }
        if self.tool:
            data["tool"] = self.tool.value
        if self.kind:
            data["kind"] = self.kind.value
        if self.suggestion:
            data["suggestion"] = self.suggestion
        if self.documentation:
            data["documentation"] = self.documentation
        return data


def resource_id(tool: ToolId, kind: ResourceKind, name: str) -> str:
    return f"{tool.value}:{kind.value}:{name}"
