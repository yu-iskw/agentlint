from __future__ import annotations

from dataclasses import dataclass

from agentlint.models import Severity


@dataclass(frozen=True)
class RuleInfo:
    code: str
    title: str
    default_severity: Severity
    description: str
    remediation: str


RULES: dict[str, RuleInfo] = {
    "SCHEMA.MISSING_FIELD": RuleInfo(
        code="SCHEMA.MISSING_FIELD",
        title="Missing required schema field",
        default_severity=Severity.ERROR,
        description="A required field declared by an adapter schema is missing.",
        remediation="Add the required field with a valid value.",
    ),
    "SCHEMA.INVALID_TYPE": RuleInfo(
        code="SCHEMA.INVALID_TYPE",
        title="Invalid field type",
        default_severity=Severity.ERROR,
        description="A field value has the wrong type for the adapter schema.",
        remediation="Change field value to the expected type.",
    ),
    "SCHEMA.INVALID_ENUM": RuleInfo(
        code="SCHEMA.INVALID_ENUM",
        title="Invalid enum value",
        default_severity=Severity.ERROR,
        description="A field value is outside the supported enum values.",
        remediation="Use one of the documented enum values.",
    ),
    "SCHEMA.UNKNOWN_FIELD": RuleInfo(
        code="SCHEMA.UNKNOWN_FIELD",
        title="Unknown field",
        default_severity=Severity.WARNING,
        description="The field is not recognized by the adapter schema.",
        remediation="Fix typo or remove unsupported field.",
    ),
    "GRAPH.MISSING_TARGET": RuleInfo(
        code="GRAPH.MISSING_TARGET",
        title="Missing reference target",
        default_severity=Severity.ERROR,
        description="A refs selector did not resolve to any resource.",
        remediation="Create the target resource or update refs selector.",
    ),
    "GRAPH.AMBIGUOUS_TARGET": RuleInfo(
        code="GRAPH.AMBIGUOUS_TARGET",
        title="Ambiguous reference target",
        default_severity=Severity.ERROR,
        description="A refs selector resolved to multiple resources.",
        remediation="Specify tool/kind/path in refs selector.",
    ),
    "GRAPH.INVALID_TARGET_KIND": RuleInfo(
        code="GRAPH.INVALID_TARGET_KIND",
        title="Invalid reference target kind",
        default_severity=Severity.ERROR,
        description="A refs selector declared a kind that does not match resolved resource.",
        remediation="Align refs.kind with the target resource kind.",
    ),
    "GRAPH.CYCLE_DETECTED": RuleInfo(
        code="GRAPH.CYCLE_DETECTED",
        title="Cycle detected",
        default_severity=Severity.ERROR,
        description="A disallowed cycle exists in the resource reference graph.",
        remediation="Break the cycle or configure cycle policy.",
    ),
    "SEC.POSSIBLE_SECRET_IN_METADATA": RuleInfo(
        code="SEC.POSSIBLE_SECRET_IN_METADATA",
        title="Possible secret in metadata",
        default_severity=Severity.WARNING,
        description="Potential secret-like literals found in metadata/frontmatter.",
        remediation="Move secret values to secure secret storage.",
    ),
    "SEC.OVERBROAD_TOOL_PERMISSION": RuleInfo(
        code="SEC.OVERBROAD_TOOL_PERMISSION",
        title="Overbroad tool permission",
        default_severity=Severity.WARNING,
        description="Tool permissions are configured too broadly.",
        remediation="Reduce tool permissions to least privilege.",
    ),
    "SEC.HOOK_OUTPUT_CONTRACT": RuleInfo(
        code="SEC.HOOK_OUTPUT_CONTRACT",
        title="Hook output contract",
        default_severity=Severity.WARNING,
        description="Hook output appears incompatible with JSON output contracts.",
        remediation="Set hook output contract to JSON.",
    ),
}


RULESETS: dict[str, set[str]] = {
    "core": {
        "SCHEMA.MISSING_FIELD",
        "SCHEMA.INVALID_TYPE",
        "SCHEMA.INVALID_ENUM",
        "SCHEMA.UNKNOWN_FIELD",
        "GRAPH.MISSING_TARGET",
        "GRAPH.AMBIGUOUS_TARGET",
        "GRAPH.INVALID_TARGET_KIND",
        "GRAPH.CYCLE_DETECTED",
    },
    "security-lite": {
        "SEC.POSSIBLE_SECRET_IN_METADATA",
        "SEC.OVERBROAD_TOOL_PERMISSION",
        "SEC.HOOK_OUTPUT_CONTRACT",
    },
    "security-strict": {
        "SEC.POSSIBLE_SECRET_IN_METADATA",
        "SEC.OVERBROAD_TOOL_PERMISSION",
        "SEC.HOOK_OUTPUT_CONTRACT",
    },
}


def rule_enabled(code: str, rulesets: list[str]) -> bool:
    enabled: set[str] = set()
    for ruleset in rulesets:
        enabled |= RULESETS.get(ruleset, set())
    return code in enabled
