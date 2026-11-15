"""OpenRouter adapter tests. No network: httpx.MockTransport answers instead."""

import json
from decimal import Decimal

import httpx
import pytest

from agent.llm.base import InvalidResponse, ProviderError, ProviderTimeout, RateLimited
from agent.llm.openrouter import OpenRouterLLM


def make_llm(handler):
    client = httpx.Client(transport=httpx.MockTransport(handler))
    return OpenRouterLLM(api_key="test-key", model="test/model:free", client=client)


def ok(body):
    return lambda request: httpx.Response(200, json=body)


def test_text_answer_with_usage_and_cost():
    llm = make_llm(ok({
        "id": "gen-123",
        "model": "test/model:free",
        "choices": [{"message": {"role": "assistant", "content": "Hello"}}],
        "usage": {"prompt_tokens": 12, "completion_tokens": 3, "cost": 0.0001},
    }))

    resp = llm.complete([{"role": "user", "content": "hi"}])

    assert resp.text == "Hello"
    assert resp.usage.input_tokens == 12
    assert resp.usage.output_tokens == 3
    assert resp.cost == Decimal("0.0001")  # exact, no float noise
    assert resp.provider_request_id == "gen-123"


def test_tool_call_arguments_are_parsed_from_json_string():
    llm = make_llm(ok({
        "id": "gen-1",
        "choices": [{"message": {"content": None, "tool_calls": [{
            "id": "call_1",
            "type": "function",
            "function": {"name": "get_order_status", "arguments": '{"order_number": 123}'},
        }]}}],
    }))

    resp = llm.complete([{"role": "user", "content": "where is #123?"}])

    assert resp.text is None
    (call,) = resp.tool_calls
    assert (call.id, call.name, call.arguments) == ("call_1", "get_order_status", {"order_number": 123})


def test_missing_usage_is_unknown_not_zero():
    llm = make_llm(ok({"choices": [{"message": {"content": "Hi"}}]}))

    resp = llm.complete([{"role": "user", "content": "hi"}])

    assert resp.usage is None
    assert resp.cost is None


def test_request_sends_key_model_and_tools():
    seen = {}

    def handler(request):
        seen["auth"] = request.headers["Authorization"]
        seen["body"] = json.loads(request.content)
        return httpx.Response(200, json={"choices": [{"message": {"content": "ok"}}]})

    tools = [{"type": "function", "function": {"name": "get_order_status", "parameters": {}}}]
    make_llm(handler).complete([{"role": "user", "content": "hi"}], tools=tools)

    assert seen["auth"] == "Bearer test-key"
    assert seen["body"]["model"] == "test/model:free"
    assert seen["body"]["tools"] == tools


def test_429_becomes_rate_limited_with_retry_after():
    llm = make_llm(lambda r: httpx.Response(429, headers={"Retry-After": "7"}))

    with pytest.raises(RateLimited) as exc:
        llm.complete([{"role": "user", "content": "hi"}])
    assert exc.value.retry_after == 7.0


def test_server_error_message_has_status_only_not_body():
    llm = make_llm(lambda r: httpx.Response(500, text="secret-ish details from provider"))

    with pytest.raises(ProviderError) as exc:
        llm.complete([{"role": "user", "content": "hi"}])
    assert "500" in str(exc.value)
    assert "secret" not in str(exc.value)


def test_timeout_becomes_provider_timeout():
    def handler(request):
        raise httpx.ReadTimeout("slow", request=request)

    with pytest.raises(ProviderTimeout):
        make_llm(handler).complete([{"role": "user", "content": "hi"}])


def test_200_with_error_inside_is_a_provider_error():
    llm = make_llm(ok({"error": {"code": 502, "message": "upstream down"}}))

    with pytest.raises(ProviderError):
        llm.complete([{"role": "user", "content": "hi"}])


@pytest.mark.parametrize("body", [{"choices": []}, {"unexpected": True}])
def test_no_choices_is_invalid_response(body):
    with pytest.raises(InvalidResponse):
        make_llm(ok(body)).complete([{"role": "user", "content": "hi"}])


def test_broken_tool_arguments_are_invalid_response():
    llm = make_llm(ok({"choices": [{"message": {"tool_calls": [{
        "id": "c1", "function": {"name": "get_order_status", "arguments": "{not json"},
    }]}}]}))

    with pytest.raises(InvalidResponse):
        llm.complete([{"role": "user", "content": "hi"}])


def test_empty_key_refuses_to_build():
    with pytest.raises(ValueError):
        OpenRouterLLM(api_key="", model="x")
