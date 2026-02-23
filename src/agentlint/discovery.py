from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

from agentlint.config import Config
from agentlint.models import ToolId


@dataclass(frozen=True)
class DiscoveredFile:
    tool: ToolId
    path: Path


def _iter_matches(root: Path, includes: list[str], excludes: list[str]) -> set[Path]:
    matches: set[Path] = set()
    for pattern in includes:
        matches.update(root.glob(pattern))
    for pattern in excludes:
        for excluded in root.glob(pattern):
            matches.discard(excluded)
    return matches


def discover_files(
    cwd: Path,
    config: Config,
    selected_tools: set[ToolId] | None = None,
    changed_files: Iterable[Path] | None = None,
) -> list[DiscoveredFile]:
    changed_set = {path.resolve() for path in changed_files} if changed_files else None
    limits = config.raw.get("limits", {})
    max_size_bytes = int(limits.get("max_file_size_kb", 2048)) * 1024
    follow_symlinks = bool(limits.get("follow_symlinks", False))

    discovered: list[DiscoveredFile] = []
    for tool_name, tool_cfg in config.raw.get("tools", {}).items():
        tool = ToolId(tool_name)
        if selected_tools and tool not in selected_tools:
            continue
        if not tool_cfg.get("enabled", True):
            continue

        roots: list[str] = tool_cfg.get("roots", [])
        includes: list[str] = tool_cfg.get("include", ["**/*"])
        excludes: list[str] = tool_cfg.get("exclude", [])

        for root_item in roots:
            root = Path(root_item).expanduser()
            if not root.is_absolute():
                root = cwd / root
            if not root.exists():
                continue

            for path in sorted(_iter_matches(root, includes, excludes)):
                if path.is_dir():
                    continue
                if not follow_symlinks and path.is_symlink():
                    continue
                if path.stat().st_size > max_size_bytes:
                    continue
                if changed_set and path.resolve() not in changed_set:
                    continue
                discovered.append(DiscoveredFile(tool=tool, path=path))

    discovered.sort(key=lambda item: (item.tool.value, str(item.path)))
    return discovered
