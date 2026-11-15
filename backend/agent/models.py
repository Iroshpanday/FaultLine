import uuid

from django.db import models
from django.db.models import Q


class AgentRunStatus(models.TextChoices):
    PENDING = "pending", "Pending"
    SUCCEEDED = "succeeded", "Succeeded"
    FAILED = "failed", "Failed"


class AgentRun(models.Model):
    """One logical agent turn: a customer question in, one answer out.

    Created as PENDING *before* any provider call, so a crash mid-call
    still leaves a row we can find and investigate.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    store = models.ForeignKey(
        "stores.Store", on_delete=models.PROTECT, related_name="agent_runs"
    )
    idempotency_key = models.CharField(max_length=100)
    status = models.CharField(
        max_length=20, choices=AgentRunStatus.choices, default=AgentRunStatus.PENDING
    )
    steps = models.PositiveSmallIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    finished_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["store", "idempotency_key"],
                name="agent_run_idempotency_key_unique_per_store",
            ),
            models.CheckConstraint(
                condition=Q(status__in=AgentRunStatus.values),
                name="agent_run_status_valid",
            ),
            # pending  <=> not finished yet. A "succeeded" run with no
            # finished_at (or a pending one with it) is a bug.
            models.CheckConstraint(
                condition=(
                    Q(status=AgentRunStatus.PENDING, finished_at__isnull=True)
                    | (~Q(status=AgentRunStatus.PENDING) & Q(finished_at__isnull=False))
                ),
                name="agent_run_finished_at_matches_status",
            ),
        ]

    def __str__(self):
        return f"AgentRun {self.id} ({self.status})"


class LLMCallStatus(models.TextChoices):
    PENDING = "pending", "Pending"
    SUCCEEDED = "succeeded", "Succeeded"
    FAILED = "failed", "Failed"


class LLMErrorCategory(models.TextChoices):
    TIMEOUT = "timeout", "Timeout"
    RATE_LIMITED = "rate_limited", "Rate limited"
    PROVIDER_ERROR = "provider_error", "Provider error"
    INVALID_RESPONSE = "invalid_response", "Invalid response"


class CostSource(models.TextChoices):
    PROVIDER = "provider", "Reported by provider"
    ESTIMATED = "estimated", "Estimated from our price table"
    UNKNOWN = "unknown", "Unknown"


class LLMCall(models.Model):
    """One request to an LLM provider. Every retry/fallback is its own row.

    Created as PENDING before the request is sent. Tokens and cost are
    NULL when unknown, never 0: 0 would claim the call was free.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    agent_run = models.ForeignKey(
        AgentRun, on_delete=models.PROTECT, related_name="llm_calls"
    )
    attempt_number = models.PositiveSmallIntegerField()
    provider = models.CharField(max_length=50)
    model = models.CharField(max_length=100)
    provider_request_id = models.CharField(max_length=200, blank=True)
    status = models.CharField(
        max_length=20, choices=LLMCallStatus.choices, default=LLMCallStatus.PENDING
    )
    error_category = models.CharField(
        max_length=30, choices=LLMErrorCategory.choices, blank=True
    )
    latency_ms = models.PositiveIntegerField(null=True, blank=True)
    input_tokens = models.PositiveIntegerField(null=True, blank=True)
    output_tokens = models.PositiveIntegerField(null=True, blank=True)
    cost = models.DecimalField(max_digits=12, decimal_places=8, null=True, blank=True)
    currency = models.CharField(max_length=3, default="USD")
    cost_source = models.CharField(
        max_length=20, choices=CostSource.choices, default=CostSource.UNKNOWN
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["agent_run", "attempt_number"],
                name="llm_call_attempt_unique_per_run",
            ),
            models.CheckConstraint(
                condition=Q(attempt_number__gte=1),
                name="llm_call_attempt_starts_at_1",
            ),
            models.CheckConstraint(
                condition=Q(status__in=LLMCallStatus.values),
                name="llm_call_status_valid",
            ),
            # An error category only makes sense on a failed call, and a
            # failed call must say why.
            models.CheckConstraint(
                condition=(
                    (Q(status=LLMCallStatus.FAILED) & ~Q(error_category=""))
                    | (~Q(status=LLMCallStatus.FAILED) & Q(error_category=""))
                ),
                name="llm_call_error_category_only_when_failed",
            ),
            models.CheckConstraint(
                condition=Q(cost__isnull=True) | Q(cost__gte=0),
                name="llm_call_cost_not_negative",
            ),
        ]

    def __str__(self):
        return f"LLMCall #{self.attempt_number} {self.model} ({self.status})"
