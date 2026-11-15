"""Tools the agent may call. The model picks a tool and its arguments;
our code decides what that tool is allowed to see.

Rule: the store ALWAYS comes from our side (the request), never from the
model's arguments. A model that could pass store_id could read any tenant (E2).
"""

from typing import Any

from commerce.models import Order
from stores.models import Store

GET_ORDER_STATUS_SPEC = {
    "type": "function",
    "function": {
        "name": "get_order_status",
        "description": "Look up the status of a customer's order by its order number.",
        "parameters": {
            "type": "object",
            "properties": {
                "order_number": {
                    "type": "integer",
                    "description": "The order number, e.g. 123 for order #123.",
                }
            },
            "required": ["order_number"],
        },
    },
}


def get_order_status(store: Store, arguments: dict[str, Any]) -> dict[str, Any]:
    # The model may send 123, "123" or "#123". Accept those; reject anything else.
    raw = str(arguments.get("order_number", "")).strip().lstrip("#")
    if not raw.isdigit():
        return {"error": "order_number must be a whole number, e.g. 123"}
    number = int(raw)

    order = Order.objects.filter(store=store, number=number).first()
    if order is None:
        # "Not found" is a normal answer, not a crash: the model can tell the
        # customer instead of inventing a status (E12).
        return {"found": False, "order_number": number}

    # Only what the answer needs. No customer email/name in the prompt.
    return {
        "found": True,
        "order_number": order.number,
        "status": order.status,
        "placed_at": order.placed_at.date().isoformat(),
        "total": str(order.total),
        "currency": order.currency,
    }


# name -> (spec sent to the model, function we run)
TOOLS = {
    "get_order_status": (GET_ORDER_STATUS_SPEC, get_order_status),
}


def tool_specs() -> list[dict[str, Any]]:
    return [spec for spec, _ in TOOLS.values()]


def run_tool(store: Store, name: str, arguments: dict[str, Any]) -> dict[str, Any]:
    """Run a tool the model asked for. Unknown names are an answer, not a crash."""
    if name not in TOOLS:
        return {"error": f"unknown tool: {name}"}
    _, func = TOOLS[name]
    return func(store, arguments)
