from __future__ import annotations

from pathlib import Path
from typing import Any

from agentlint.adapters.base import Adapter, ParsedArtifact, SchemaDefinition
from agentlint.models import Resource, ResourceKind, ToolId


class CursorAdapter(Adapter):
    """Adapter for Cursor resources."""

    id = ToolId.CURSOR

    def identify_kind(self, path: Path, parsed: ParsedArtifact) -> ResourceKind:
        hint = str(parsed.frontmatter.get("kind", "")).lower()
        if hint in {kind.value for kind in ResourceKind}:
            return ResourceKind(hint)
        if "subagents" in path.parts:
            return ResourceKind.SUBAGENT
        if "skills" in path.parts:
            return ResourceKind.SKILL
        return ResourceKind.UNKNOWN

    def schema(self, resource: Resource) -> SchemaDefinition:
        required = {"name"} if resource.content_type.value == "markdown" else set()
        allowed = {"name", "description", "kind", "version", "tags", "refs", "tools"}
        types: dict[str, tuple[type[Any], ...]] = {
            "name": (str,),
            "description": (str,),
            "kind": (str,),
            "version": (str, int),
            "tags": (list,),
            "refs": (list,),
            "tools": (list, str),
        }
        return SchemaDefinition(
            required_fields=required, field_types=types, allowed_fields=allowed
        )
