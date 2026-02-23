from __future__ import annotations

from pathlib import Path
from typing import Any

from agentlint.adapters.base import Adapter, ParsedArtifact, SchemaDefinition
from agentlint.models import ContentType, Resource, ResourceKind, ToolId


class GeminiAdapter(Adapter):
    """Adapter for Gemini resources."""

    id = ToolId.GEMINI

    def identify_kind(self, path: Path, parsed: ParsedArtifact) -> ResourceKind:
        hint = str(
            parsed.frontmatter.get("kind", parsed.metadata.get("kind", ""))
        ).lower()
        if hint in {kind.value for kind in ResourceKind}:
            return ResourceKind(hint)
        if parsed.content_type in {ContentType.JSON, ContentType.YAML}:
            if "hook" in path.stem or "hooks" in path.parts:
                return ResourceKind.HOOK
            return ResourceKind.CONFIG
        if "skills" in path.parts:
            return ResourceKind.SKILL
        return ResourceKind.UNKNOWN

    def schema(self, resource: Resource) -> SchemaDefinition:
        required = {"name"}
        if resource.kind == ResourceKind.HOOK:
            required = {"name", "trigger"}
        allowed = {
            "name",
            "description",
            "kind",
            "version",
            "tags",
            "refs",
            "trigger",
            "tool_permissions",
            "output_format",
        }
        types: dict[str, tuple[type[Any], ...]] = {
            "name": (str,),
            "description": (str,),
            "kind": (str,),
            "version": (str, int),
            "tags": (list,),
            "refs": (list,),
            "trigger": (str,),
            "tool_permissions": (str, list, dict),
            "output_format": (str,),
        }
        return SchemaDefinition(
            required_fields=required, field_types=types, allowed_fields=allowed
        )
