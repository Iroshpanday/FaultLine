"""The agent loop, driven by FakeLLM. No network, no key, same result every run."""

import json

import pytest

from agent.llm.base import ProviderTimeout, RateLimited, Usage
from agent.llm.fake import CallTool, FakeLLM, Raise, Reply
from agent.models import AgentRun, LLMCall
from agent.services import DuplicateRun, run_agent
from commerce.factories import OrderFactory

pytestmark = pytest.mark.django_db

QUESTION = "Where is my order #123?"


def test_order_question_calls_the_tool_then_answers():
    order = OrderFactory(number=123, status="shipped")
    llm = FakeLLM([
        CallTool("get_order_status", {"order_number": 123}),
        Reply("Your order #123 has shipped."),
    ])

    result = run_agent(order.store, QUESTION, "key-1", llm)

    assert result.answer == "Your order #123 has shipped."
    assert result.run.status == "succeeded"
    assert result.run.finished_at is not None
    assert result.run.steps == 2

    # The second LLM request carried the real tool result from our DB.
    tool_message = llm.calls[1].messages[-1]
    assert tool_message["role"] == "tool"
    assert json.loads(tool_message["content"])["status"] == "shipped"


def test_every_llm_request_is_logged_as_a_row():
    order = OrderFactory(number=123)
    llm = FakeLLM([
        CallTool("get_order_status", {"order_number": 123}),
        Reply("Shipped.", usage=None),
    ])

    run = run_agent(order.store, QUESTION, "key-1", llm).run

    calls = list(run.llm_calls.order_by("attempt_number"))
    assert [c.attempt_number for c in calls] == [1, 2]
    assert all(c.status == "succeeded" for c in calls)
    assert (calls[0].input_tokens, calls[0].output_tokens) == (10, 5)
    assert calls[1].input_tokens is None  # not reported -> unknown, not 0


def test_provider_timeout_fails_the_run_and_records_why():
    order = OrderFactory()
    llm = FakeLLM([Raise(ProviderTimeout)])

    result = run_agent(order.store, QUESTION, "key-1", llm)

    assert result.answer is None
    assert result.run.status == "failed"
    call = result.run.llm_calls.get()
    assert (call.status, call.error_category) == ("failed", "timeout")
    assert call.latency_ms is not None


def test_rate_limit_is_recorded_as_rate_limited():
    order = OrderFactory()

    run = run_agent(order.store, QUESTION, "key-1", FakeLLM([Raise(RateLimited(retry_after=5))])).run

    assert run.llm_calls.get().error_category == "rate_limited"


def test_a_model_that_never_stops_calling_tools_is_cut_off():
    order = OrderFactory(number=123)
    llm = FakeLLM([CallTool("get_order_status", {"order_number": 123})] * 3)

    result = run_agent(order.store, QUESTION, "key-1", llm, max_steps=3)

    assert result.run.status == "failed"
    assert result.run.llm_calls.count() == 3


def test_same_idempotency_key_does_not_call_the_llm_again():
    order = OrderFactory()
    run_agent(order.store, QUESTION, "key-1", FakeLLM([Reply("Hi")]))
    second_llm = FakeLLM([Reply("should never be used")])

    with pytest.raises(DuplicateRun):
        run_agent(order.store, QUESTION, "key-1", second_llm)

    assert second_llm.calls == []
    assert AgentRun.objects.count() == 1
    assert LLMCall.objects.count() == 1


def test_unreported_cost_stays_unknown():
    # FakeLLM reports no cost, so the row must say "unknown", not "free".
    order = OrderFactory()

    run = run_agent(order.store, QUESTION, "key-1", FakeLLM([Reply("Hi", usage=Usage(1, 1))])).run

    call = run.llm_calls.get()
    assert call.cost is None and call.cost_source == "unknown"  # fake reports no cost
