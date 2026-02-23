from __future__ import annotations

from agentlint.adapters.base import SchemaDefinition
from agentlint.models import Issue, Resource, Severity


def validate_schema(resource: Resource, schema: SchemaDefinition) -> list[Issue]:
    issues: list[Issue] = []
    frontmatter = resource.frontmatter

    for field in sorted(schema.required_fields):
        if field not in frontmatter and field not in resource.metadata:
            issues.append(
                Issue(
                    severity=Severity.ERROR,
                    code="SCHEMA.MISSING_FIELD",
                    message=f"Missing required field: {field}",
                    path=resource.path,
                    span=resource.locations.get(field),
                    tool=resource.tool,
                    kind=resource.kind,
                    suggestion=f"Add '{field}: ...' to frontmatter or metadata.",
                )
            )

    source = dict(resource.metadata)
    source.update(frontmatter)
    for field, value in source.items():
        if field in schema.field_types and not isinstance(
            value, schema.field_types[field]
        ):
            expected = ", ".join(sorted(t.__name__ for t in schema.field_types[field]))
            issues.append(
                Issue(
                    severity=Severity.ERROR,
                    code="SCHEMA.INVALID_TYPE",
                    message=f"Field '{field}' must be one of: {expected}",
                    path=resource.path,
                    span=resource.locations.get(field),
                    tool=resource.tool,
                    kind=resource.kind,
                    suggestion=f"Adjust field '{field}' to the expected type.",
                )
            )

    for field in frontmatter:
        if field not in schema.allowed_fields:
            issues.append(
                Issue(
                    severity=Severity.WARNING,
                    code="SCHEMA.UNKNOWN_FIELD",
                    message=f"Unknown field: {field}",
                    path=resource.path,
                    span=resource.locations.get(field),
                    tool=resource.tool,
                    kind=resource.kind,
                    suggestion="Remove typo or add field in adapter schema.",
                )
            )

    return issues
