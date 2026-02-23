from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from agentlint.adapters import build_adapters
from agentlint.adapters.base import ParsedArtifact
from agentlint.config import Config, load_config
from agentlint.discovery import discover_files
from agentlint.graph import detect_cycles, validate_references
from agentlint.models import ContentType, Issue, RefType, Resource, Severity, ToolId
from agentlint.parsers.markdown import FrontmatterError, parse_markdown
from agentlint.parsers.structured import ParseError, parse_json, parse_yaml, read_text
from agentlint.plugins import run_plugin_rules
from agentlint.rules.core import validate_schema
from agentlint.rules.registry import RULES, rule_enabled
from agentlint.rules.security_lite import run_security_lite


@dataclass(frozen=True)
class CheckResult:
    resources: list[Resource]
    issues: list[Issue]


def _parse_artifact(path: Path) -> ParsedArtifact:
    suffix = path.suffix.lower()
    raw = read_text(path)
    if suffix == ".md":
        document = parse_markdown(raw)
        return ParsedArtifact(
            content_type=ContentType.MARKDOWN,
            frontmatter=document.frontmatter,
            body=document.body,
            metadata={},
            locations=document.locations,
        )
    if suffix in {".yaml", ".yml"}:
        parsed = parse_yaml(raw)
        return ParsedArtifact(
            content_type=ContentType.YAML,
            frontmatter={},
            body=raw,
            metadata=parsed,
            locations={},
        )
    if suffix == ".json":
        parsed = parse_json(raw)
        return ParsedArtifact(
            content_type=ContentType.JSON,
            frontmatter={},
            body=raw,
            metadata=parsed,
            locations={},
        )
    return ParsedArtifact(
        content_type=ContentType.TEXT,
        frontmatter={},
        body=raw,
        metadata={},
        locations={},
    )


def _apply_severities(issues: list[Issue], config: Config) -> list[Issue]:
    overrides = config.severities()
    adjusted: list[Issue] = []
    for issue in issues:
        if issue.code in overrides:
            adjusted.append(
                Issue(
                    severity=overrides[issue.code],
                    code=issue.code,
                    message=issue.message,
                    path=issue.path,
                    span=issue.span,
                    tool=issue.tool,
                    kind=issue.kind,
                    suggestion=issue.suggestion,
                    documentation=issue.documentation,
                )
            )
        else:
            adjusted.append(issue)
    return adjusted


def _severity_rank(severity: Severity) -> int:
    return {Severity.INFO: 1, Severity.WARNING: 2, Severity.ERROR: 3}[severity]


def has_failures(issues: list[Issue], fail_on: Severity) -> bool:
    threshold = _severity_rank(fail_on)
    return any(_severity_rank(issue.severity) >= threshold for issue in issues)


def run_check(
    cwd: Path,
    config_path: Path | None,
    selected_tools: set[ToolId] | None,
    rulesets_override: list[str] | None,
    changed_files: list[Path] | None,
    ci: bool,
) -> CheckResult:
    config = load_config(cwd=cwd, config_path=config_path, ci=ci)
    rulesets = rulesets_override or list(
        config.raw.get("validation", {}).get("rulesets", ["core"])
    )

    discovered = discover_files(
        cwd=cwd,
        config=config,
        selected_tools=selected_tools,
        changed_files=changed_files,
    )
    adapters = build_adapters()

    issues: list[Issue] = []
    resources: list[Resource] = []

    for item in discovered:
        adapter = adapters[item.tool.value]
        try:
            parsed = _parse_artifact(item.path)
            resource = adapter.to_resource(item.path, parsed)
            resources.append(resource)
        except (ParseError, FrontmatterError) as exc:
            issues.append(
                Issue(
                    severity=Severity.ERROR,
                    code="SCHEMA.INVALID_TYPE",
                    message=str(exc),
                    path=item.path,
                    suggestion="Fix parsing errors and ensure UTF-8 content.",
                )
            )

    for resource in resources:
        adapter = adapters[resource.tool.value]
        schema = adapter.schema(resource)
        for issue in validate_schema(resource, schema):
            if rule_enabled(issue.code, rulesets):
                issues.append(issue)
        if rule_enabled("SEC.POSSIBLE_SECRET_IN_METADATA", rulesets):
            for issue in run_security_lite(resource):
                if rule_enabled(issue.code, rulesets):
                    issues.append(issue)

    cross_tool_refs = bool(
        config.raw.get("validation", {}).get("cross_tool_refs", False)
    )
    graph_issues, edges = validate_references(
        resources, cross_tool_refs=cross_tool_refs
    )
    for issue in graph_issues:
        if rule_enabled(issue.code, rulesets):
            issues.append(issue)

    allow_cycles = bool(
        config.raw.get("validation", {}).get("graph", {}).get("allow_cycles", False)
    )
    if not allow_cycles:
        allowed = {
            RefType(value)
            for value in config.raw.get("validation", {})
            .get("graph", {})
            .get("cycle_ref_types_allowed", [])
            if value in {ref.value for ref in RefType}
        }
        for issue in detect_cycles(resources, edges, allowed_ref_types=allowed):
            if rule_enabled(issue.code, rulesets):
                issues.append(issue)

    issues.extend(
        run_plugin_rules(
            resources=resources, config=config, rulesets=rulesets, rule_catalog=RULES
        )
    )

    adjusted = _apply_severities(issues, config)
    adjusted.sort(key=lambda item: (str(item.path), item.code, item.message))
    return CheckResult(resources=resources, issues=adjusted)
