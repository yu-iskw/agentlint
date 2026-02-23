from __future__ import annotations

import json

from agentlint.models import Issue
from agentlint.rules.registry import RULES


def render_sarif(issues: list[Issue]) -> str:
    rules: dict[str, dict[str, object]] = {}
    results: list[dict[str, object]] = []

    for issue in issues:
        if issue.code not in rules:
            info = RULES.get(issue.code)
            rules[issue.code] = {
                "id": issue.code,
                "name": issue.code,
                "shortDescription": {"text": info.title if info else issue.code},
                "fullDescription": {
                    "text": info.description if info else issue.message
                },
                "help": {"text": info.remediation if info else "See project docs."},
            }

        result: dict[str, object] = {
            "ruleId": issue.code,
            "level": "error" if issue.severity.value == "error" else "warning",
            "message": {"text": issue.message},
            "locations": [
                {
                    "physicalLocation": {
                        "artifactLocation": {"uri": str(issue.path)},
                        "region": {
                            "startLine": issue.span.line_start if issue.span else 1,
                            "startColumn": issue.span.col_start if issue.span else 1,
                        },
                    }
                }
            ],
        }
        results.append(result)

    sarif_payload = {
        "$schema": "https://json.schemastore.org/sarif-2.1.0.json",
        "version": "2.1.0",
        "runs": [
            {
                "tool": {
                    "driver": {
                        "name": "agentlint",
                        "informationUri": "https://github.com/yu/local-agentlint",
                        "rules": list(rules.values()),
                    }
                },
                "results": results,
            }
        ],
    }
    return json.dumps(sarif_payload, indent=2, sort_keys=True)
