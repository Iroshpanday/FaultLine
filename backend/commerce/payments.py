"""The boundary between Faultline and a payment provider (refunds).

Like the LLM adapter, our code talks to PaymentGateway only. A real provider
(Stripe, Khalti, eSewa) implements it later; tests use FakePaymentGateway,
which can reproduce the one failure E1 is about, on demand.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from decimal import Decimal


class PaymentError(Exception):
    """Base for every payment failure our code must handle."""


class PaymentTimeout(PaymentError, TimeoutError):
    """We stopped waiting for the provider's reply.

    It does NOT mean the refund failed. The provider may have paid it out and
    only the reply got lost. From our side the outcome is unknown.
    """


@dataclass(frozen=True)
class RefundReceipt:
    provider_ref: str  # the provider's id for the refund, e.g. "re_0001"


class PaymentGateway(ABC):
    @abstractmethod
    def refund(
        self, *, order_ref: str, amount: Decimal, currency: str, idempotency_key: str | None = None
    ) -> RefundReceipt:
        """Send money back. One attempt; never retries by itself.

        idempotency_key: real providers accept one. A second call with the same
        key returns the first refund's receipt instead of paying out again.
        """


class FakePaymentGateway(PaymentGateway):
    """An in-memory provider for tests.

        gateway = FakePaymentGateway(late_replies=1)   # rush hour: the next reply is late

    `payouts` is what the provider actually sent to customers: the source of
    truth a test checks, whatever our own database says.
    """

    def __init__(self, *, late_replies: int = 0):
        self.payouts: list[dict] = []
        self._late_replies = late_replies
        self._by_key: dict[str, RefundReceipt] = {}

    def refund(
        self, *, order_ref: str, amount: Decimal, currency: str, idempotency_key: str | None = None
    ) -> RefundReceipt:
        # Seen this key before: the provider returns the original refund and pays nothing.
        if idempotency_key is not None and idempotency_key in self._by_key:
            return self._by_key[idempotency_key]

        # The money moves FIRST...
        receipt = RefundReceipt(provider_ref=f"re_{len(self.payouts) + 1:04d}")
        self.payouts.append({"ref": receipt.provider_ref, "order": order_ref, "amount": amount, "currency": currency})
        if idempotency_key is not None:
            self._by_key[idempotency_key] = receipt

        # ...then, at rush hour, the reply never reaches us in time.
        if self._late_replies > 0:
            self._late_replies -= 1
            raise PaymentTimeout("no reply from the payment provider in time")
        return receipt

    @property
    def total_paid_out(self) -> Decimal:
        return sum((p["amount"] for p in self.payouts), Decimal("0"))
