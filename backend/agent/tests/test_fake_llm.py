import pytest

from agent.llm.base import ProviderTimeout, RateLimited, ToolCallRequest
from agent.llm.fake import CallTool, FakeLLM, Raise, Reply, ScriptExhausted

USER_MSG = [{"role": "user", "content": "Where is my order?"}]


def test_steps_are_returned_in_script_order():
    llm = FakeLLM([CallTool("get_order_status", {"order_id": "o-1"}), Reply("It shipped.")])

    first = llm.complete(USER_MSG)
    second = llm.complete(USER_MSG)

    assert first.tool_calls == (ToolCallRequest("get_order_status", {"order_id": "o-1"}, id="call_1"),)
    assert first.text is None
    assert second.text == "It shipped."
    assert llm.remaining_steps == 0


def test_scripted_errors_are_raised():
    llm = FakeLLM([Raise(ProviderTimeout), Raise(RateLimited(retry_after=2))])

    with pytest.raises(ProviderTimeout):
        llm.complete(USER_MSG)
    with pytest.raises(RateLimited) as exc:
        llm.complete(USER_MSG)
    assert exc.value.retry_after == 2


def test_missing_usage_stays_none_not_zero():
    llm = FakeLLM([Reply("ok", usage=None)])

    assert llm.complete(USER_MSG).usage is None


def test_calling_past_the_script_fails_loudly():
    llm = FakeLLM([Reply("only one")])
    llm.complete(USER_MSG)

    with pytest.raises(ScriptExhausted):
        llm.complete(USER_MSG)


def test_recorded_calls_are_snapshots():
    llm = FakeLLM([Reply("a"), Reply("b")])
    messages = list(USER_MSG)

    llm.complete(messages)
    messages.append({"role": "assistant", "content": "a"})
    llm.complete(messages)

    assert len(llm.calls[0].messages) == 1
    assert len(llm.calls[1].messages) == 2
 