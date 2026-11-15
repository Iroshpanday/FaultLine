"""Deterministic stand-in for a real LLM, driven by a script.

    llm = FakeLLM([
        CallTool("get_order_status", {"order_id": "..."}),
        Reply("Your order shipped yesterday."),
    ])

Each complete() call consumes the next step. Running past the end fails the
test loudly, which is how a runaway agent loop shows up in tests (E3).
"""

import copy
from dataclasses import dataclass
from typing import Any

from .base import LLMAdapter, LLMResponse, Message, ProviderError, ToolCallRequest, ToolSpec, Usage

FAKE_MODEL = "fake/scripted-model"
DEFAULT_USAGE = Usage(input_tokens=10, output_tokens=5)


@dataclass(frozen=True)
class Reply:
    text: str
    usage: Usage | None = DEFAULT_USAGE


@dataclass(frozen=True)
class CallTool:
    name: str
    arguments: dict[str, Any]
    usage: Usage | None = DEFAULT_USAGE


@dataclass(frozen=True)
class Raise:
    error: ProviderError | type[ProviderError]


FakeStep = Reply | CallTool | Raise


class ScriptExhausted(AssertionError):
    """The code under test called the LLM more times than the script allows.
    An AssertionError, not a ProviderError, so no retry logic can swallow it."""


@dataclass(frozen=True)
class RecordedCall:
    messages: list[Message]
    tools: list[ToolSpec] | None


class FakeLLM(LLMAdapter):
    provider = "fake"
    model = FAKE_MODEL

    def __init__(self, script: list[FakeStep]):
        self._script = list(script)
        self.calls: list[RecordedCall] = []

    def complete(self, messages: list[Message], tools: list[ToolSpec] | None = None) -> LLMResponse:
        # Deep copy: the agent loop keeps appending to its message list, and a
        # test must see what was actually sent at the time of this call.
        self.calls.append(RecordedCall(copy.deepcopy(messages), copy.deepcopy(tools)))

        if not self._script:
            raise ScriptExhausted(f"FakeLLM script exhausted after {len(self.calls) - 1} call(s)")
        step = self._script.pop(0)

        match step:
            case Reply(text=text, usage=usage):
                return LLMResponse(model=FAKE_MODEL, text=text, usage=usage)
            case CallTool(name=name, arguments=arguments, usage=usage):
                call = ToolCallRequest(
                    name=name, arguments=copy.deepcopy(arguments), id=f"call_{len(self.calls)}"
                )
                return LLMResponse(model=FAKE_MODEL, tool_calls=(call,), usage=usage)
            case Raise(error=error):
                raise error
            case _:
                raise TypeError(f"not a FakeStep: {step!r}")

    @property
    def remaining_steps(self) -> int:
        return len(self._script)
