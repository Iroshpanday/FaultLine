"""The boundary between Faultline and any LLM provider.

The agent loop only talks to LLMAdapter. Real providers (OpenRouter, Phase 2)
and the FakeLLM (tests) both implement it, so tests mock at this boundary and
never touch the network.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from decimal import Decimal
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
    # The provider's id for this call. The tool result we send back must
    # quote it, so the model knows which call the result answers.
    id: str = ""


@dataclass(frozen=True)
class LLMResponse:
    model: str
    text: str | None = None
    tool_calls: tuple[ToolCallRequest, ...] = field(default_factory=tuple)
    usage: Usage | None = None
    # Lets us match our LLMCall row to the provider's own logs and bill.
    provider_request_id: str = ""
    # USD as reported by the provider. None = not reported (never 0).
    cost: Decimal | None = None


class ProviderError(Exception):
    """Base for every provider failure the agent loop must handle."""


class ProviderTimeout(ProviderError):
    """No answer within our timeout. The provider may still have done the work."""


class RateLimited(ProviderError):
    """HTTP 429. retry_after is the provider's hint in seconds, if it sent one."""

    def __init__(self, retry_after: float | None = None):
        super().__init__(f"rate limited (retry_after={retry_after})")
        self.retry_after = retry_after


class InvalidResponse(ProviderError):
    """The provider answered, but not in a shape we can use (bad JSON, no choices)."""


class LLMAdapter(ABC):
    # Recorded on every LLMCall row, so each adapter must say who it is.
    provider: str
    model: str

    @abstractmethod
    def complete(self, messages: list[Message], tools: list[ToolSpec] | None = None) -> LLMResponse:
        """One provider attempt. Raises ProviderError subclasses; never retries internally."""
