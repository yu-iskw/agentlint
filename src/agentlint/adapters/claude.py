from __future__ import annotations

from pathlib import Path
from typing import Any

from agentlint.adapters.base import Adapter, ParsedArtifact, SchemaDefinition
from agentlint.models import Resource, ResourceKind, ToolId


class ClaudeAdapter(Adapter):
    """Adapter for Claude resources."""

    id = ToolId.CLAUDE

    def identify_kind(self, path: Path, parsed: ParsedArtifact) -> ResourceKind:
        hint = str(parsed.frontmatter.get("kind", "")).lower()
        if hint in {kind.value for kind in ResourceKind}:
            return ResourceKind(hint)
        if path.name == "SKILL.md" or "skills" in path.parts:
            return ResourceKind.SKILL
        if "agents" in path.parts:
            return ResourceKind.SUBAGENT
        if "hooks" in path.parts:
            return ResourceKind.HOOK
        return ResourceKind.UNKNOWN

    def schema(self, resource: Resource) -> SchemaDefinition:
        required = {"name"} if resource.content_type.value == "markdown" else set()
        allowed = {
            "name",
            "description",
            "kind",
            "version",
            "tags",
            "refs",
            "tool_permissions",
        }
        types: dict[str, tuple[type[Any], ...]] = {
            "name": (str,),
            "description": (str,),
            "kind": (str,),
            "version": (str, int),
            "tags": (list,),
            "refs": (list,),
            "tool_permissions": (str, list, dict),
        }
        return SchemaDefinition(
            required_fields=required, field_types=types, allowed_fields=allowed
        )
