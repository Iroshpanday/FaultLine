import pytest

from agent.tools import get_order_status, run_tool
from commerce.factories import OrderFactory
from stores.factories import StoreFactory

pytestmark = pytest.mark.django_db


def test_found_order_returns_only_what_the_answer_needs():
    order = OrderFactory(number=123, status="shipped")

    result = get_order_status(order.store, {"order_number": 123})

    assert result["found"] is True
    assert result["status"] == "shipped"
    assert "email" not in result and "customer" not in result


def test_other_stores_order_is_not_visible():
    # Store B has order #123. Asking from store A must not find it.
    OrderFactory(number=123)
    store_a = StoreFactory()

    assert get_order_status(store_a, {"order_number": 123}) == {"found": False, "order_number": 123}


@pytest.mark.parametrize("value", [123, "123", "#123", " 123 "])
def test_number_formats_the_model_may_send(value):
    order = OrderFactory(number=123)

    assert get_order_status(order.store, {"order_number": value})["found"] is True


@pytest.mark.parametrize("arguments", [{}, {"order_number": "abc"}, {"order_number": -5}])
def test_bad_arguments_return_an_error_the_model_can_read(arguments):
    assert "error" in get_order_status(StoreFactory(), arguments)


def test_unknown_tool_is_an_answer_not_a_crash():
    assert run_tool(StoreFactory(), "delete_database", {}) == {"error": "unknown tool: delete_database"}
