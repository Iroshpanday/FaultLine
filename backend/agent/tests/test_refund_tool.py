"""The refund tool when nothing goes wrong, and who may use it.
(What happens when the provider is slow is E1's failing test.)"""

import json
from decimal import Decimal

import pytest

from agent.llm.fake import CallTool, FakeLLM, Reply
from agent.services import run_agent
from agent.tools import ToolContext, run_tool, tool_specs
from commerce.factories import CustomerFactory, OrderFactory
from commerce.models import Refund
from commerce.payments import FakePaymentGateway

pytestmark = pytest.mark.django_db


def ask_for_refund(order, gateway, email=None, number=None):
    llm = FakeLLM([
        CallTool("refund_order", {"order_number": number or order.number, "reason": "arrived cold"}),
        Reply("Done, your refund is on its way."),
    ])
    result = run_agent(
        order.store, "Please refund my order", "key-1", llm,
        customer_email=email or order.customer.email, payments=gateway,
    )
    return result, llm


def test_a_refund_pays_out_once_and_is_recorded():
    order = OrderFactory(number=123, total=Decimal("1250.00"))
    gateway = FakePaymentGateway()

    result, llm = ask_for_refund(order, gateway)

    assert result.run.status == "succeeded"
    assert gateway.total_paid_out == Decimal("1250.00")
    refund = Refund.objects.get()
    assert (refund.status, refund.amount, refund.provider_ref) == ("succeeded", Decimal("1250.00"), "re_0001")
    assert json.loads(llm.calls[1].messages[-1]["content"])["refunded"] is True


def test_someone_elses_order_cannot_be_refunded():
    order = OrderFactory(number=123)
    stranger = CustomerFactory(store=order.store)
    gateway = FakePaymentGateway()

    ask_for_refund(order, gateway, email=stranger.email)

    assert gateway.payouts == []
    assert not Refund.objects.exists()


def test_refunds_are_not_offered_without_a_payment_gateway():
    # The public chat passes no gateway: the model never even hears of refund_order.
    order = OrderFactory()
    ctx = ToolContext(store=order.store, customer_email=order.customer.email)

    assert [s["function"]["name"] for s in tool_specs(ctx)] == ["get_order_status"]
    assert run_tool(ctx, "refund_order", {"order_number": order.number}) == {"error": "unknown tool: refund_order"}
    assert not Refund.objects.exists()


@pytest.mark.parametrize("amount", ["0", "-5", "999999", "abc"])
def test_impossible_amounts_are_refused(amount):
    order = OrderFactory(total=Decimal("1250.00"))
    gateway = FakePaymentGateway()
    ctx = ToolContext(store=order.store, customer_email=order.customer.email, payments=gateway)

    assert "error" in run_tool(ctx, "refund_order", {"order_number": order.number, "amount": amount})
    assert gateway.payouts == []
