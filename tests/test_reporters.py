import json
from pathlib import Path

from agentlint.models import Issue, Severity
from agentlint.reporters.sarif import render_sarif


def test_sarif_report_structure() -> None:
    issues = [
        Issue(
            severity=Severity.ERROR,
            code="SCHEMA.MISSING_FIELD",
            message="Missing field",
            path=Path("foo.md"),
        )
    ]
    payload = json.loads(render_sarif(issues))
    assert payload["version"] == "2.1.0"  # nosec B101
    assert (
        payload["runs"][0]["results"][0]["ruleId"] == "SCHEMA.MISSING_FIELD"
    )  # nosec B101
