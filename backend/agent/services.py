"""The agent loop: one customer question in, one answer out.

    run = run_agent(store, "Where is my order #123?", idempotency_key, llm,
                    customer_email="demo.customer@example.com")

Writes, in this order, each committed on its own:
  1. AgentRun (pending)                    before any provider call
  2. LLMCall (pending) -> succeeded/failed  one row per provider request
  3. AgentRun -> succeeded/failed           at the end

There is deliberately NO transaction around this function. A provider call
takes seconds; holding a DB transaction open that long ties up a connection,
and a crash would roll back the pending rows that tell us what happened.

Identity: the shopper gives the email used at checkout; the tool only
returns orders for that email (order number + email, like a guest order
lookup page). The email never goes into the prompt.

v1 limits (on purpose, each is a later episode): no retries, one tool,
chat history is sent by the browser (not stored server-side yet).
"""

import json
import time
from dataclasses import dataclass

from django.db import IntegrityError, transaction
from django.utils import timezone

from stores.models import Store

from .llm.base import (
    InvalidResponse,
    LLMAdapter,
    LLMResponse,
    ProviderError,
    ProviderTimeout,
    RateLimited,
)
from .models import AgentRun, AgentRunStatus, CostSource, LLMCall, LLMCallStatus, LLMErrorCategory
from .tools import ToolContext, run_tool, tool_specs

MAX_STEPS = 5  # a model that keeps calling tools forever gets stopped here (E3)

SYSTEM_PROMPT = (
    "You are the customer support assistant for the online store {store_name}. "
    "The customer is already identified by the email they gave when the chat "
    "started; never ask for it and never mention it. "
    "To answer a question about an order, call get_order_status with the order "
    "number; it only returns this customer's own orders. "
    "Never guess or invent an order status, date or amount. If an order is not "
    "found, say you couldn't find that order number on their account and ask "
    "them to check it. If a question is not about their orders, say briefly "
    "that you can help with order status and that the store team can help "
    "with anything else. "
    "Reply in plain text without markdown, in at most three short sentences."
)

MAX_HISTORY = 10  # earlier turns the browser may send back for context


class DuplicateRun(Exception):
    """This idempotency key was already used for this store."""

    def __init__(self, run: AgentRun):
        super().__init__(f"duplicate idempotency key for run {run.id}")
        self.run = run


@dataclass(frozen=True)
class AgentResult:
    run: AgentRun
    answer: str | None  # None when the run failed


def run_agent(
    store: Store,
    question: str,
    idempotency_key: str,
    llm: LLMAdapter,
    *,
    customer_email: str,
    history: list[dict] | None = None,
    max_steps: int = MAX_STEPS,
) -> AgentResult:
    # 1. Pending row first. The unique (store, key) constraint turns a
    #    double-click or a client retry into an error instead of a second bill.
    #    atomic() = a savepoint, so a failed insert doesn't poison an outer
    #    transaction (e.g. a test, or ATOMIC_REQUESTS later).
    try:
        with transaction.atomic():
            run = AgentRun.objects.create(store=store, idempotency_key=idempotency_key)
    except IntegrityError:
        raise DuplicateRun(
            AgentRun.objects.get(store=store, idempotency_key=idempotency_key)
        ) from None

    ctx = ToolContext(store=store, customer_email=customer_email)
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT.format(store_name=store.name)},
        *_safe_history(history),
        {"role": "user", "content": question},
    ]

    for step in range(1, max_steps + 1):
        run.steps = step
        run.save(update_fields=["steps"])

        response = _call_llm(run, step, llm, messages)
        if response is None:  # provider failed; already recorded
            return _finish(run, AgentRunStatus.FAILED, answer=None)

        if not response.tool_calls:
            return _finish(run, AgentRunStatus.SUCCEEDED, answer=response.text or "")

        # The model asked for tools: run them and send the results back.
        messages.append(_assistant_message(response))
        for call in response.tool_calls:
            result = run_tool(ctx, call.name, call.arguments)
            messages.append(
                {"role": "tool", "tool_call_id": call.id, "content": json.dumps(result)}
            )

    # Out of steps: the model never gave a final answer.
    return _finish(run, AgentRunStatus.FAILED, answer=None)


def _call_llm(run: AgentRun, attempt: int, llm: LLMAdapter, messages: list) -> LLMResponse | None:
    """One provider request, bracketed by its LLMCall row. Returns None on failure."""
    call = LLMCall.objects.create(
        agent_run=run, attempt_number=attempt, provider=llm.provider, model=llm.model
    )
    started = time.monotonic()
    try:
        response = llm.complete(messages, tools=tool_specs())
    except ProviderError as exc:
        call.status = LLMCallStatus.FAILED
        call.error_category = _error_category(exc)
        call.latency_ms = _elapsed_ms(started)
        call.save(update_fields=["status", "error_category", "latency_ms"])
        return None

    call.status = LLMCallStatus.SUCCEEDED
    call.latency_ms = _elapsed_ms(started)
    call.model = response.model
    call.provider_request_id = response.provider_request_id
    if response.usage is not None:
        call.input_tokens = response.usage.input_tokens
        call.output_tokens = response.usage.output_tokens
    if response.cost is not None:
        call.cost = response.cost
        call.cost_source = CostSource.PROVIDER
    call.save()
    return response


def _safe_history(history: list[dict] | None) -> list[dict]:
    """Earlier turns from the browser. Untrusted, so only plain user/assistant
    text gets through: no system or tool messages can be smuggled in. Even a
    faked assistant turn can't reach another customer's order, because the
    tool checks the email from the request, not anything in the chat."""
    safe = [
        {"role": item["role"], "content": str(item["content"])}
        for item in (history or [])
        if item.get("role") in ("user", "assistant") and item.get("content")
    ]
    return safe[-MAX_HISTORY:]


def _finish(run: AgentRun, status: str, answer: str | None) -> AgentResult:
    run.status = status
    run.finished_at = timezone.now()
    run.save(update_fields=["status", "finished_at"])
    return AgentResult(run=run, answer=answer)


def _assistant_message(response: LLMResponse) -> dict:
    # The model must see its own tool request before the tool results.
    return {
        "role": "assistant",
        "content": response.text,
        "tool_calls": [
            {
                "id": call.id,
                "type": "function",
                "function": {"name": call.name, "arguments": json.dumps(call.arguments)},
            }
            for call in response.tool_calls
        ],
    }


def _error_category(exc: ProviderError) -> str:
    # Subclasses first: every one of these is also a ProviderError.
    if isinstance(exc, ProviderTimeout):
        return LLMErrorCategory.TIMEOUT
    if isinstance(exc, RateLimited):
        return LLMErrorCategory.RATE_LIMITED
    if isinstance(exc, InvalidResponse):
        return LLMErrorCategory.INVALID_RESPONSE
    return LLMErrorCategory.PROVIDER_ERROR


def _elapsed_ms(started: float) -> int:
    return round((time.monotonic() - started) * 1000)
