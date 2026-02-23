from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping

from agentlint.models import (
    ContentType,
    Reference,
    RefType,
    Resource,
    ResourceKind,
    ResourceSelector,
    ToolId,
    resource_id,
)


@dataclass(frozen=True)
class SchemaDefinition:
    """Adapter-level schema contract for a normalized resource."""

    required_fields: set[str]
    field_types: Mapping[str, tuple[type[Any], ...]]
    allowed_fields: set[str]


@dataclass(frozen=True)
class ParsedArtifact:
    content_type: ContentType
    frontmatter: dict[str, Any]
    body: str
    metadata: dict[str, Any]
    locations: dict[str, Any]


class Adapter(ABC):
    """Base adapter contract for ecosystem-specific resource handling."""

    id: ToolId

    @abstractmethod
    def identify_kind(self, path: Path, parsed: ParsedArtifact) -> ResourceKind:
        pass

    @abstractmethod
    def schema(self, resource: Resource) -> SchemaDefinition:
        pass

    def to_resource(self, path: Path, parsed: ParsedArtifact) -> Resource:
        kind = self.identify_kind(path, parsed)
        name = str(
            parsed.frontmatter.get("name") or parsed.metadata.get("name") or path.stem
        )
        metadata = dict(parsed.metadata)
        refs = self.extract_references(
            from_id=resource_id(self.id, kind, name),
            refs_obj=parsed.frontmatter.get("refs"),
            default_tool=self.id,
        )
        return Resource(
            id=resource_id(self.id, kind, name),
            tool=self.id,
            kind=kind,
            name=name,
            path=path,
            content_type=parsed.content_type,
            frontmatter=parsed.frontmatter,
            body=parsed.body,
            metadata=metadata,
            refs=refs,
            locations=parsed.locations,
        )

    def extract_references(
        self, from_id: str, refs_obj: Any, default_tool: ToolId
    ) -> list[Reference]:
        references: list[Reference] = []
        if refs_obj is None:
            return references
        if not isinstance(refs_obj, list):
            return references

        for item in refs_obj:
            selector = ResourceSelector(tool=default_tool)
            ref_type = RefType.USES
            raw = str(item)

            if isinstance(item, str):
                selector = ResourceSelector(tool=default_tool, name=item)
            elif isinstance(item, dict):
                tool = default_tool
                if item.get("tool"):
                    try:
                        tool = ToolId(str(item["tool"]))
                    except ValueError:
                        tool = default_tool
                kind = None
                if item.get("kind"):
                    try:
                        kind = ResourceKind(str(item["kind"]))
                    except ValueError:
                        kind = None
                if item.get("ref_type"):
                    try:
                        ref_type = RefType(str(item["ref_type"]))
                    except ValueError:
                        ref_type = RefType.USES
                selector = ResourceSelector(
                    tool=tool,
                    kind=kind,
                    name=item.get("name"),
                    path=item.get("path"),
                )
                raw = str(item)

            references.append(
                Reference(
                    from_id=from_id,
                    to_selector=selector,
                    ref_type=ref_type,
                    raw=raw,
                )
            )
        return references
