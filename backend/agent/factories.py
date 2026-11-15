from decimal import Decimal

import factory

from stores.factories import StoreFactory

from .models import AgentRun, CostSource, LLMCall, LLMCallStatus


class AgentRunFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = AgentRun

    store = factory.SubFactory(StoreFactory)
    idempotency_key = factory.Sequence(lambda n: f"run-{n}")


class LLMCallFactory(factory.django.DjangoModelFactory):
    """A finished, successful call by default. Override fields to test failures."""

    class Meta:
        model = LLMCall

    agent_run = factory.SubFactory(AgentRunFactory)
    attempt_number = 1
    provider = "openrouter"
    model = "test/model"
    status = LLMCallStatus.SUCCEEDED
    latency_ms = 120
    input_tokens = 10
    output_tokens = 5
    cost = Decimal("0.00001000")
    cost_source = CostSource.PROVIDER
