"""The boundary between Faultline and any LLM provider.

The agent loop only talks to LLMAdapter. Real providers (OpenRouter, Phase 2)
and the FakeLLM (tests) both implement it, so tests mock at this boundary and
never touch the network.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any

Message = dict[str, Any]  # OpenAI-style: {"role": "user", "content": "..."}
ToolSpec = dict[str, Any]  # JSON schema of a tool the model may call


@dataclass(frozen=True)
class Usage:
    # None means the provider did not report it. Never coerce to 0: a 0 would
    # make cost look free and hide the gap (E9).
    input_tokens: int | None
    output_tokens: int | None


@dataclass(frozen=True)
class ToolCallRequest:
    name: str
    arguments: dict[str, Any]


@dataclass(frozen=True)
class LLMResponse:
    model: str
    text: str | None = None
    tool_calls: tuple[ToolCallRequest, ...] = field(default_factory=tuple)
    usage: Usage | None = None


class ProviderError(Exception):
    """Base for every provider failure the agent loop must handle."""


class ProviderTimeout(ProviderError):
    """No answer within our timeout. The provider may still have done the work."""


class RateLimited(ProviderError):
    """HTTP 429. retry_after is the provider's hint in seconds, if it sent one."""

    def __init__(self, retry_after: float | None = None):
        super().__init__(f"rate limited (retry_after={retry_after})")
        self.retry_after = retry_after


class LLMAdapter(ABC):
    @abstractmethod
    def complete(self, messages: list[Message], tools: list[ToolSpec] | None = None) -> LLMResponse:
        """One provider attempt. Raises ProviderError subclasses; never retries internally."""
