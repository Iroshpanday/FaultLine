import pytest

from agent.tools import ToolContext, get_order_status, run_tool
from commerce.factories import CustomerFactory, OrderFactory
from stores.factories import StoreFactory

pytestmark = pytest.mark.django_db


def ctx_for(order):
    """The context a real request would build for the order's own customer."""
    return ToolContext(store=order.store, customer_email=order.customer.email)


def test_found_order_returns_only_what_the_answer_needs():
    order = OrderFactory(number=123, status="shipped")

    result = get_order_status(ctx_for(order), {"order_number": 123})

    assert result["found"] is True
    assert result["status"] == "shipped"
    assert "email" not in result and "customer" not in result


def test_email_match_ignores_case():
    order = OrderFactory(number=123, customer__email="Demo@Example.com")
    ctx = ToolContext(store=order.store, customer_email="demo@example.COM")

    assert get_order_status(ctx, {"order_number": 123})["found"] is True


def test_another_customers_order_looks_exactly_like_a_missing_one():
    # Same store, real order #123, but it belongs to someone else.
    order = OrderFactory(number=123)
    stranger = CustomerFactory(store=order.store, email="stranger@example.com")
    ctx = ToolContext(store=order.store, customer_email=stranger.email)

    someone_elses = get_order_status(ctx, {"order_number": 123})
    missing = get_order_status(ctx, {"order_number": 999})

    assert someone_elses == {"found": False, "order_number": 123}
    assert missing == {"found": False, "order_number": 999}  # same shape: nothing to probe


def test_other_stores_order_is_not_visible():
    # Store B has order #123 for this email. Asking from store A must not find it.
    order = OrderFactory(number=123)
    ctx = ToolContext(store=StoreFactory(), customer_email=order.customer.email)

    assert get_order_status(ctx, {"order_number": 123}) == {"found": False, "order_number": 123}


@pytest.mark.parametrize("value", [123, "123", "#123", " 123 "])
def test_number_formats_the_model_may_send(value):
    order = OrderFactory(number=123)

    assert get_order_status(ctx_for(order), {"order_number": value})["found"] is True


@pytest.mark.parametrize("arguments", [{}, {"order_number": "abc"}, {"order_number": -5}])
def test_bad_arguments_return_an_error_the_model_can_read(arguments):
    ctx = ToolContext(store=StoreFactory(), customer_email="a@example.com")

    assert "error" in get_order_status(ctx, arguments)


def test_unknown_tool_is_an_answer_not_a_crash():
    ctx = ToolContext(store=StoreFactory(), customer_email="a@example.com")

    assert run_tool(ctx, "delete_database", {}) == {"error": "unknown tool: delete_database"}
