from __future__ import annotations

from dataclasses import dataclass

EXIT_OK = 0
EXIT_ISSUES = 1
EXIT_CONFIG_ERROR = 2
EXIT_INTERNAL_ERROR = 3


class AgentlintError(Exception):
    """Base class for agentlint exceptions."""


class AgentlintConfigError(AgentlintError):
    """Raised when config is invalid."""


@dataclass(frozen=True)
class ExitDecision:
    code: int
    reason: str
