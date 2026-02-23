from __future__ import annotations

from pathlib import Path

import typer
import yaml  # type: ignore[import-untyped]

from agentlint.config import CONFIG_FILENAME, DEFAULT_CONFIG, ConfigError
from agentlint.engine import has_failures, run_check
from agentlint.errors import (
    EXIT_CONFIG_ERROR,
    EXIT_INTERNAL_ERROR,
    EXIT_ISSUES,
    EXIT_OK,
)
from agentlint.models import Severity, ToolId
from agentlint.reporters.human import render_human
from agentlint.reporters.json import render_json
from agentlint.reporters.sarif import render_sarif
from agentlint.rules.registry import RULES

app = typer.Typer(help="Static linter for coding-agent resources")
CONFIG_OPTION = typer.Option(None, "--config", help="Path to .agentlint.yaml")
TOOL_OPTION = typer.Option(None, "--tool", help="Comma-separated tools")
RULESET_OPTION = typer.Option(None, "--ruleset", help="Comma-separated rulesets")
OUTPUT_FORMAT_OPTION = typer.Option(
    "human", "--format", help="Output format(s), comma-separated"
)
FAIL_ON_OPTION = typer.Option(
    Severity.ERROR, "--fail-on", help="Failure severity threshold"
)
CHANGED_FILES_OPTION = typer.Option([], "--changed-files", help="Scoped file list")
CI_OPTION = typer.Option(False, "--ci", help="CI mode")
FORCE_OPTION = typer.Option(False, "--force", help="Overwrite existing config")


def _parse_tools(value: str | None) -> set[ToolId] | None:
    if not value:
        return None
    tools: set[ToolId] = set()
    for item in value.split(","):
        item = item.strip()
        if not item:
            continue
        tools.add(ToolId(item))
    return tools


def _parse_csv(value: str | None) -> list[str] | None:
    if not value:
        return None
    return [item.strip() for item in value.split(",") if item.strip()]


@app.command()
def check(
    config: Path | None = CONFIG_OPTION,
    tool: str | None = TOOL_OPTION,
    ruleset: str | None = RULESET_OPTION,
    output_format: str = OUTPUT_FORMAT_OPTION,
    fail_on: Severity = FAIL_ON_OPTION,
    changed_files: list[Path] = CHANGED_FILES_OPTION,
    ci: bool = CI_OPTION,
) -> None:
    try:
        selected_tools = _parse_tools(tool)
        formats = _parse_csv(output_format) or ["human"]
        rulesets = _parse_csv(ruleset)
        result = run_check(
            cwd=Path.cwd(),
            config_path=config,
            selected_tools=selected_tools,
            rulesets_override=rulesets,
            changed_files=changed_files or None,
            ci=ci,
        )
    except ConfigError as exc:
        typer.echo(f"Config error: {exc}", err=True)
        raise typer.Exit(code=EXIT_CONFIG_ERROR) from exc
    except Exception as exc:  # pylint: disable=broad-except
        typer.echo(f"Internal error: {exc}", err=True)
        raise typer.Exit(code=EXIT_INTERNAL_ERROR) from exc

    rendered: list[str] = []
    for item in formats:
        if item == "human":
            rendered.append(render_human(result.issues))
        elif item == "json":
            rendered.append(render_json(result.issues))
        elif item == "sarif":
            rendered.append(render_sarif(result.issues))
        else:
            typer.echo(f"Unsupported format: {item}", err=True)
            raise typer.Exit(code=EXIT_CONFIG_ERROR)
    typer.echo("\n".join(rendered))

    if has_failures(result.issues, fail_on):
        raise typer.Exit(code=EXIT_ISSUES)
    raise typer.Exit(code=EXIT_OK)


@app.command("dump-resources")
def dump_resources(
    config: Path | None = CONFIG_OPTION,
    tool: str | None = TOOL_OPTION,
    ci: bool = CI_OPTION,
) -> None:
    selected_tools = _parse_tools(tool)
    result = run_check(
        cwd=Path.cwd(),
        config_path=config,
        selected_tools=selected_tools,
        rulesets_override=["core"],
        changed_files=None,
        ci=ci,
    )
    typer.echo(render_json(result.issues, result.resources))


@app.command()
def explain(rule_id: str) -> None:
    rule = RULES.get(rule_id)
    if not rule:
        typer.echo(f"Unknown rule: {rule_id}", err=True)
        raise typer.Exit(code=EXIT_CONFIG_ERROR)
    typer.echo(f"{rule.code} ({rule.default_severity.value})")
    typer.echo(rule.title)
    typer.echo(rule.description)
    typer.echo(f"Remediation: {rule.remediation}")


@app.command()
def init(force: bool = FORCE_OPTION) -> None:
    destination = Path.cwd() / CONFIG_FILENAME
    if destination.exists() and not force:
        typer.echo(
            f"{CONFIG_FILENAME} already exists. Use --force to overwrite.", err=True
        )
        raise typer.Exit(code=EXIT_CONFIG_ERROR)
    destination.write_text(
        yaml.safe_dump(DEFAULT_CONFIG, sort_keys=False), encoding="utf-8"
    )
    typer.echo(f"Created {destination}")


if __name__ == "__main__":
    app()
