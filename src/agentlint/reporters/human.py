from __future__ import annotations

from collections import defaultdict

from agentlint.models import Issue


def render_human(issues: list[Issue]) -> str:
    if not issues:
        return "No issues found."

    grouped: dict[str, list[Issue]] = defaultdict(list)
    for issue in issues:
        grouped[str(issue.path)].append(issue)

    lines: list[str] = []
    for path in sorted(grouped):
        lines.append(path)
        for issue in grouped[path]:
            location = ""
            if issue.span:
                location = f":{issue.span.line_start}:{issue.span.col_start}"
            lines.append(f"  {issue.severity.value.upper()} {issue.code}{location}")
            lines.append(f"    {issue.message}")
            if issue.suggestion:
                lines.append(f"    Suggestion: {issue.suggestion}")

    counts: dict[str, int] = defaultdict(int)
    for issue in issues:
        counts[issue.severity.value] += 1
    lines.append("")
    lines.append(
        "Summary: "
        + ", ".join(
            f"{counts[key]} {key}"
            for key in ["error", "warning", "info"]
            if key in counts
        )
    )
    return "\n".join(lines)
