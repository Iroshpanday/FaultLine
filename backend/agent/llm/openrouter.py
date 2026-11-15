"""OpenRouter adapter: exactly one HTTP request per complete() call.

No SDK on purpose: SDKs retry silently, and a hidden retry is a hidden
charge (E9). Retries belong to the agent loop, where each attempt gets
its own LLMCall row.
"""

import json
from decimal import Decimal

import httpx

from .base import (
    InvalidResponse,
    LLMAdapter,
    LLMResponse,
    Message,
    ProviderError,
    ProviderTimeout,
    RateLimited,
    ToolCallRequest,
    ToolSpec,
    Usage,
)

API_URL = "https://openrouter.ai/api/v1/chat/completions"


class OpenRouterLLM(LLMAdapter):
    provider = "openrouter"

    def __init__(
        self,
        api_key: str,
        model: str,
        timeout: float = 30.0,
        client: httpx.Client | None = None,
    ):
        if not api_key:
            raise ValueError("OPENROUTER_API_KEY is empty")
        self.model = model
        self._api_key = api_key
        # Tests pass a client with a fake transport, so no network is used.
        self._client = client or httpx.Client(timeout=timeout)

    def complete(self, messages: list[Message], tools: list[ToolSpec] | None = None) -> LLMResponse:
        payload = {
            "model": self.model,
            "messages": messages,
            "usage": {"include": True},  # ask OpenRouter to report the cost
        }
        if tools:
            payload["tools"] = tools

        try:
            resp = self._client.post(
                API_URL,
                json=payload,
                headers={"Authorization": f"Bearer {self._api_key}"},
            )
        except httpx.TimeoutException:
            raise ProviderTimeout("no response from OpenRouter in time") from None
        except httpx.HTTPError as exc:
            raise ProviderError(f"network error: {type(exc).__name__}") from None

        if resp.status_code == 429:
            raise RateLimited(retry_after=_retry_after(resp))
        if resp.status_code >= 400:
            # Status code only. Error bodies can echo request data; never log them.
            raise ProviderError(f"OpenRouter HTTP {resp.status_code}")

        return self._parse(resp)

    def _parse(self, resp: httpx.Response) -> LLMResponse:
        try:
            data = resp.json()
        except ValueError:
            raise InvalidResponse("response was not JSON") from None

        # OpenRouter can answer 200 with an upstream provider's error inside.
        if isinstance(data, dict) and "error" in data:
            error = data["error"]
            code = error.get("code") if isinstance(error, dict) else None
            raise ProviderError(f"upstream error (code={code})")

        try:
            message = data["choices"][0]["message"]
        except (KeyError, IndexError, TypeError):
            raise InvalidResponse("no choices in response") from None

        usage = data.get("usage") or {}
        cost = usage.get("cost")
        return LLMResponse(
            model=data.get("model") or self.model,
            text=message.get("content") or None,
            tool_calls=tuple(_parse_tool_call(tc) for tc in message.get("tool_calls") or []),
            usage=Usage(usage.get("prompt_tokens"), usage.get("completion_tokens")) if usage else None,
            provider_request_id=data.get("id") or "",
            # str() first: Decimal(0.1) keeps float noise, Decimal("0.1") does not.
            cost=Decimal(str(cost)) if cost is not None else None,
        )


def _parse_tool_call(tc: dict) -> ToolCallRequest:
    try:
        fn = tc["function"]
        arguments = json.loads(fn.get("arguments") or "{}")
        name = fn["name"]
    except (KeyError, TypeError, json.JSONDecodeError):
        raise InvalidResponse("malformed tool call") from None
    if not isinstance(arguments, dict):
        raise InvalidResponse("tool arguments are not a JSON object")
    return ToolCallRequest(name=name, arguments=arguments, id=tc.get("id") or "")


def _retry_after(resp: httpx.Response) -> float | None:
    try:
        return float(resp.headers["Retry-After"])
    except (KeyError, ValueError):
        return None
