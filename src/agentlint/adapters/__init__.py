from agentlint.adapters.base import Adapter
from agentlint.adapters.claude import ClaudeAdapter
from agentlint.adapters.codex import CodexAdapter
from agentlint.adapters.cursor import CursorAdapter
from agentlint.adapters.gemini import GeminiAdapter


def build_adapters() -> dict[str, Adapter]:
    adapters = [ClaudeAdapter(), CursorAdapter(), GeminiAdapter(), CodexAdapter()]
    return {adapter.id.value: adapter for adapter in adapters}
