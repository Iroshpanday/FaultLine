"""Tools the agent may call. The model picks a tool and its arguments;
our code decides what that tool is allowed to see.

Rule: who is asking (store + customer email) ALWAYS comes from our side
(the request), never from the model's arguments. A model that could pass
store_id or an email could read any tenant or any customer (E2).
"""

from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from typing import Any

from commerce.models import Order, Refund, RefundStatus
from commerce.payments import PaymentGateway
from stores.models import Store


@dataclass(frozen=True)
class ToolContext:
    store: Store
    customer_email: str  # given by the shopper at the start of the chat
    # Refunds are offered only when the caller passes a gateway. The public chat never
    # does (no approvals yet), so a shopper can't talk the agent into a refund.
    payments: PaymentGateway | None = None


GET_ORDER_STATUS_SPEC = {
    "type": "function",
    "function": {
        "name": "get_order_status",
        "description": "Look up the status of one of this customer's orders by its order number.",
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


def get_order_status(ctx: ToolContext, arguments: dict[str, Any]) -> dict[str, Any]:
    # The model may send 123, "123" or "#123". Accept those; reject anything else.
    raw = str(arguments.get("order_number", "")).strip().lstrip("#")
    if not raw.isdigit():
        return {"error": "order_number must be a whole number, e.g. 123"}
    number = int(raw)

    order = Order.objects.filter(
        store=ctx.store, number=number, customer__email__iexact=ctx.customer_email
    ).first()
    if order is None:
        # Same answer for "no such order" and "someone else's order", so nobody
        # can probe which order numbers exist. "Not found" is a normal answer,
        # not a crash: the model can say so instead of inventing one (E12).
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


REFUND_ORDER_SPEC = {
    "type": "function",
    "function": {
        "name": "refund_order",
        "description": "Refund one of this customer's orders, in full or in part.",
        "parameters": {
            "type": "object",
            "properties": {
                "order_number": {"type": "integer", "description": "The order number, e.g. 123."},
                "amount": {"type": "number", "description": "Amount to refund. Leave out for a full refund."},
                "reason": {"type": "string", "description": "Why, in a few words."},
            },
            "required": ["order_number"],
        },
    },
}


def refund_order(ctx: ToolContext, arguments: dict[str, Any]) -> dict[str, Any]:
    """NAIVE v1 (E1, written this way on purpose).

    It records the refund, asks the provider to pay it, and marks it done. It
    assumes it runs once. If the provider's reply times out, PaymentTimeout
    escapes, the agent loop retries the whole tool, and a second refund is paid.
    """
    raw = str(arguments.get("order_number", "")).strip().lstrip("#")
    if not raw.isdigit():
        return {"error": "order_number must be a whole number, e.g. 123"}
    order = Order.objects.filter(
        store=ctx.store, number=int(raw), customer__email__iexact=ctx.customer_email
    ).first()
    if order is None:
        return {"found": False, "order_number": int(raw)}

    try:
        amount = Decimal(str(arguments.get("amount") or order.total)).quantize(Decimal("0.01"))
    except InvalidOperation:
        return {"error": "amount must be a number, e.g. 250"}
    if amount <= 0 or amount > order.total:
        return {"error": f"amount must be between 0 and the order total ({order.total})"}

    refund = Refund.objects.create(
        store=ctx.store,
        order=order,
        amount=amount,
        currency=order.currency,
        reason=str(arguments.get("reason", ""))[:200],
    )
    receipt = ctx.payments.refund(order_ref=str(order.id), amount=amount, currency=order.currency)
    refund.status = RefundStatus.SUCCEEDED
    refund.provider_ref = receipt.provider_ref
    refund.save(update_fields=["status", "provider_ref"])
    return {"refunded": True, "order_number": order.number, "amount": str(amount), "currency": order.currency}


# name -> (spec sent to the model, function we run)
TOOLS = {
    "get_order_status": (GET_ORDER_STATUS_SPEC, get_order_status),
    "refund_order": (REFUND_ORDER_SPEC, refund_order),
}


def _offered(ctx: ToolContext) -> list[str]:
    names = ["get_order_status"]
    if ctx.payments is not None:
        names.append("refund_order")
    return names


def tool_specs(ctx: ToolContext) -> list[dict[str, Any]]:
    """The tools this conversation may use. The model never hears of the others."""
    return [TOOLS[name][0] for name in _offered(ctx)]


def run_tool(ctx: ToolContext, name: str, arguments: dict[str, Any]) -> dict[str, Any]:
    """Run a tool the model asked for. Unknown or unoffered names are an answer, not a crash."""
    if name not in _offered(ctx):
        return {"error": f"unknown tool: {name}"}
    _, func = TOOLS[name]
    return func(ctx, arguments)
