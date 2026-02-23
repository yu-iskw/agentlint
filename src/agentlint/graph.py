from __future__ import annotations

from collections import defaultdict

from agentlint.models import Issue, RefType, Resource, ResourceSelector, Severity, Span


def resolve_selector(
    selector: ResourceSelector,
    resources: list[Resource],
    cross_tool_refs: bool,
    from_tool: str,
) -> list[Resource]:
    candidates = resources

    if selector.tool is not None:
        candidates = [item for item in candidates if item.tool == selector.tool]
    elif not cross_tool_refs:
        candidates = [item for item in candidates if item.tool.value == from_tool]

    if selector.kind is not None:
        candidates = [item for item in candidates if item.kind == selector.kind]
    if selector.name:
        candidates = [item for item in candidates if item.name == selector.name]
    if selector.path:
        candidates = [
            item for item in candidates if str(item.path).endswith(selector.path)
        ]
    return candidates


def validate_references(
    resources: list[Resource], cross_tool_refs: bool
) -> tuple[list[Issue], list[tuple[str, str, RefType]]]:
    issues: list[Issue] = []
    edges: list[tuple[str, str, RefType]] = []

    by_id = {resource.id: resource for resource in resources}
    for resource in resources:
        for ref in resource.refs:
            matches = resolve_selector(
                selector=ref.to_selector,
                resources=resources,
                cross_tool_refs=cross_tool_refs,
                from_tool=resource.tool.value,
            )
            if not matches:
                issues.append(
                    Issue(
                        severity=Severity.ERROR,
                        code="GRAPH.MISSING_TARGET",
                        message=f"Reference target not found: {ref.raw}",
                        path=resource.path,
                        span=ref.source_span,
                        tool=resource.tool,
                        kind=resource.kind,
                        suggestion="Add the missing target or update refs entry.",
                    )
                )
                continue
            if len(matches) > 1:
                issues.append(
                    Issue(
                        severity=Severity.ERROR,
                        code="GRAPH.AMBIGUOUS_TARGET",
                        message=f"Reference target is ambiguous: {ref.raw}",
                        path=resource.path,
                        span=ref.source_span,
                        tool=resource.tool,
                        kind=resource.kind,
                        suggestion="Provide kind or path in refs selector.",
                    )
                )
                continue

            target = matches[0]
            if ref.to_selector.kind and ref.to_selector.kind != target.kind:
                issues.append(
                    Issue(
                        severity=Severity.ERROR,
                        code="GRAPH.INVALID_TARGET_KIND",
                        message=(
                            f"Reference expected kind {ref.to_selector.kind.value} "
                            f"but resolved to {target.kind.value}"
                        ),
                        path=resource.path,
                        span=ref.source_span,
                        tool=resource.tool,
                        kind=resource.kind,
                        suggestion="Fix refs.kind or target resource kind.",
                    )
                )
                continue

            if ref.from_id not in by_id:
                continue
            edges.append((ref.from_id, target.id, ref.ref_type))

    return issues, edges


def detect_cycles(
    resources: list[Resource],
    edges: list[tuple[str, str, RefType]],
    allowed_ref_types: set[RefType],
) -> list[Issue]:
    adjacency: dict[str, list[str]] = defaultdict(list)
    resource_by_id = {resource.id: resource for resource in resources}

    for source, target, ref_type in edges:
        if ref_type in allowed_ref_types:
            continue
        adjacency[source].append(target)

    issues: list[Issue] = []
    visited: set[str] = set()
    in_stack: set[str] = set()

    def visit(node: str) -> None:
        visited.add(node)
        in_stack.add(node)
        for child in adjacency.get(node, []):
            if child not in visited:
                visit(child)
            elif child in in_stack:
                resource = resource_by_id.get(node)
                if resource:
                    issues.append(
                        Issue(
                            severity=Severity.ERROR,
                            code="GRAPH.CYCLE_DETECTED",
                            message=f"Cycle detected from {node} to {child}",
                            path=resource.path,
                            span=Span(1, 1, 1, 1),
                            tool=resource.tool,
                            kind=resource.kind,
                            suggestion="Break the dependency cycle or allow this ref_type.",
                        )
                    )
        in_stack.remove(node)

    for resource in resources:
        if resource.id not in visited:
            visit(resource.id)

    return issues
