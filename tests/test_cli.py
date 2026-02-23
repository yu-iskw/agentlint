from typer.testing import CliRunner

from agentlint.cli import app


def test_explain_rule() -> None:
    runner = CliRunner()
    result = runner.invoke(app, ["explain", "GRAPH.MISSING_TARGET"])
    assert result.exit_code == 0  # nosec B101
    assert "GRAPH.MISSING_TARGET" in result.stdout  # nosec B101
