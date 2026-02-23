from pathlib import Path

from agentlint.engine import run_check


def test_run_check_fixtures_no_errors() -> None:
    fixture_root = Path(__file__).parent / "fixtures" / "claude"
    result = run_check(
        cwd=fixture_root,
        config_path=None,
        selected_tools=None,
        rulesets_override=["core"],
        changed_files=None,
        ci=True,
    )
    assert len(result.resources) >= 2  # nosec B101
    assert not [
        issue for issue in result.issues if issue.severity.value == "error"
    ]  # nosec B101


def test_run_check_detects_missing_reference(tmp_path: Path) -> None:
    skill_dir = tmp_path / ".claude" / "skills" / "missing"
    skill_dir.mkdir(parents=True)
    (skill_dir / "SKILL.md").write_text(
        "---\nname: missing-ref\nkind: skill\nrefs:\n  - name: nope\n---\ntext\n",
        encoding="utf-8",
    )
    result = run_check(
        cwd=tmp_path,
        config_path=None,
        selected_tools=None,
        rulesets_override=["core"],
        changed_files=None,
        ci=True,
    )
    codes = {issue.code for issue in result.issues}
    assert "GRAPH.MISSING_TARGET" in codes  # nosec B101
