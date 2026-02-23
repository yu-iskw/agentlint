from agentlint.parsers.markdown import parse_markdown


def test_parse_markdown_with_frontmatter() -> None:
    raw = """---
name: demo
kind: skill
---
Body\n"""
    document = parse_markdown(raw)
    assert document.frontmatter["name"] == "demo"  # nosec B101
    assert "Body" in document.body  # nosec B101
    assert "name" in document.locations  # nosec B101
