from __future__ import annotations

import re
from typing import Any

from agentlint.models import Issue, Resource, ResourceKind, Severity

_SECRET_KEY_PATTERN = re.compile(r"(token|api[_-]?key|secret|password)", re.IGNORECASE)
_SECRET_VALUE_PATTERN = re.compile(r"[A-Za-z0-9_\-]{20,}")


def _flatten_dict(data: dict[str, Any], prefix: str = "") -> list[tuple[str, Any]]:
    values: list[tuple[str, Any]] = []
    for key, value in data.items():
        qualified = f"{prefix}.{key}" if prefix else key
        if isinstance(value, dict):
            values.extend(_flatten_dict(value, qualified))
        else:
            values.append((qualified, value))
    return values


def run_security_lite(resource: Resource) -> list[Issue]:
    issues: list[Issue] = []

    combined = dict(resource.metadata)
    combined.update(resource.frontmatter)
    for key, value in _flatten_dict(combined):
        if (
            _SECRET_KEY_PATTERN.search(key)
            and isinstance(value, str)
            and _SECRET_VALUE_PATTERN.search(value)
        ):
            issues.append(
                Issue(
                    severity=Severity.WARNING,
                    code="SEC.POSSIBLE_SECRET_IN_METADATA",
                    message=f"Potential secret-like value in field '{key}'",
                    path=resource.path,
                    span=None,
                    tool=resource.tool,
                    kind=resource.kind,
                    suggestion="Move secret material to secure runtime secrets storage.",
                )
            )

    permission_value = resource.frontmatter.get(
        "tool_permissions"
    ) or resource.metadata.get("tool_permissions")
    if isinstance(permission_value, str) and permission_value.lower() in {
        "*",
        "all",
        "allow_all",
    }:
        issues.append(
            Issue(
                severity=Severity.WARNING,
                code="SEC.OVERBROAD_TOOL_PERMISSION",
                message="Overbroad tool permissions detected",
                path=resource.path,
                span=None,
                tool=resource.tool,
                kind=resource.kind,
                suggestion="Restrict tool_permissions to the minimum required set.",
            )
        )

    if resource.kind == ResourceKind.HOOK:
        output_format = resource.frontmatter.get(
            "output_format"
        ) or resource.metadata.get("output_format")
        if output_format and str(output_format).lower() != "json":
            issues.append(
                Issue(
                    severity=Severity.WARNING,
                    code="SEC.HOOK_OUTPUT_CONTRACT",
                    message="Hook output format is not JSON",
                    path=resource.path,
                    span=None,
                    tool=resource.tool,
                    kind=resource.kind,
                    suggestion="Set output_format to 'json' if adapter contract requires structured output.",
                )
            )

    return issues
