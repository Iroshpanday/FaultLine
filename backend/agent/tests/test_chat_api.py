"""POST /api/stores/<slug>/chat, with FakeLLM swapped in for the real provider."""

import pytest
from django.core.cache import cache
from rest_framework.test import APIClient
from rest_framework.throttling import ScopedRateThrottle

from agent.llm.base import ProviderTimeout
from agent.llm.fake import CallTool, FakeLLM, Raise, Reply
from agent.models import AgentRun
from commerce.factories import OrderFactory
from stores.factories import StoreFactory

pytestmark = pytest.mark.django_db


@pytest.fixture(autouse=True)
def clear_throttle_counters():
    cache.clear()  # throttle counts live in the cache; start each test at zero


@pytest.fixture
def fake_llm(monkeypatch):
    """Call fake_llm([...steps]) to decide what the 'model' answers."""
    def install(script):
        llm = FakeLLM(script)
        monkeypatch.setattr("agent.llm.build_llm", lambda: llm)
        return llm
    return install


def post_chat(slug, message, key="key-1"):
    headers = {"HTTP_IDEMPOTENCY_KEY": key} if key else {}
    return APIClient().post(f"/api/stores/{slug}/chat", {"message": message}, format="json", **headers)


def test_answers_an_order_question(fake_llm):
    order = OrderFactory(number=123, status="shipped")
    fake_llm([CallTool("get_order_status", {"order_number": 123}), Reply("It has shipped.")])

    resp = post_chat(order.store.slug, "Where is my order #123?")

    assert resp.status_code == 200
    assert resp.json()["answer"] == "It has shipped."
    assert AgentRun.objects.get(id=resp.json()["run_id"]).status == "succeeded"


def test_needs_no_login(fake_llm):
    # Shoppers aren't Django users: no session, no CSRF token, still 200.
    store = StoreFactory()
    fake_llm([Reply("Hi!")])

    assert post_chat(store.slug, "hello").status_code == 200


def test_unknown_store_is_404(fake_llm):
    llm = fake_llm([])

    assert post_chat("no-such-store", "hi").status_code == 404
    assert llm.calls == []


def test_missing_idempotency_key_is_400_and_costs_nothing(fake_llm):
    store = StoreFactory()
    llm = fake_llm([])

    assert post_chat(store.slug, "hi", key=None).status_code == 400
    assert llm.calls == []


@pytest.mark.parametrize("message", ["", "x" * 1001])
def test_empty_or_huge_message_is_400(fake_llm, message):
    store = StoreFactory()
    llm = fake_llm([])

    assert post_chat(store.slug, message).status_code == 400
    assert llm.calls == []


def test_same_key_twice_is_409_and_the_llm_runs_once(fake_llm):
    store = StoreFactory()
    llm = fake_llm([Reply("Hi!")])

    assert post_chat(store.slug, "hello", key="k").status_code == 200
    second = post_chat(store.slug, "hello", key="k")

    assert second.status_code == 409
    assert len(llm.calls) == 1


def test_provider_down_is_503_with_a_calm_message(fake_llm):
    store = StoreFactory()
    fake_llm([Raise(ProviderTimeout)])

    resp = post_chat(store.slug, "hello")

    assert resp.status_code == 503
    assert "unavailable" in resp.json()["error"]
    assert "Timeout" not in resp.json()["error"]  # internals stay in our logs


def test_too_many_requests_are_throttled(fake_llm, monkeypatch):
    # DRF copies the rates onto the class at import time, so patch it there.
    monkeypatch.setattr(ScopedRateThrottle, "THROTTLE_RATES", {"chat": "2/min"})
    store = StoreFactory()
    fake_llm([Reply("1"), Reply("2")])

    codes = [post_chat(store.slug, "hi", key=f"k{i}").status_code for i in range(3)]

    assert codes == [200, 200, 429]


def test_fake_forwarded_for_headers_do_not_reset_the_throttle(fake_llm, monkeypatch):
    # A script sending a new made-up IP each time must still be limited.
    monkeypatch.setattr(ScopedRateThrottle, "THROTTLE_RATES", {"chat": "2/min"})
    store = StoreFactory()
    fake_llm([Reply("1"), Reply("2")])
    client = APIClient()

    codes = [
        client.post(
            f"/api/stores/{store.slug}/chat", {"message": "hi"}, format="json",
            HTTP_IDEMPOTENCY_KEY=f"k{i}", HTTP_X_FORWARDED_FOR=f"10.0.0.{i}",
        ).status_code
        for i in range(3)
    ]

    assert codes == [200, 200, 429]
