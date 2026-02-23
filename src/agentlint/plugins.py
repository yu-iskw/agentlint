from __future__ import annotations

from importlib.metadata import entry_points
from typing import Mapping, Protocol

from agentlint.config import Config
from agentlint.models import Issue, Resource


class RulePlugin(Protocol):
    code: str

    def apply(self, resources: list[Resource], config: Config) -> list[Issue]:
        pass


def run_plugin_rules(
    resources: list[Resource],
    config: Config,
    rulesets: list[str],
    rule_catalog: Mapping[str, object],
) -> list[Issue]:
    if "security-strict" not in rulesets:
        return []

    loaded = entry_points(group="agentlint.rules")
    issues: list[Issue] = []
    for item in loaded:
        plugin = item.load()
        rule: RulePlugin = plugin()
        if rule.code not in rule_catalog:
            continue
        issues.extend(rule.apply(resources, config))
    return issues
