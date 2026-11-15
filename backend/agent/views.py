"""HTTP layer for the agent. Thin on purpose: validate input, call the
service, translate the result to a status code. No business logic here."""

from django.shortcuts import get_object_or_404
from rest_framework import serializers, status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.throttling import ScopedRateThrottle
from rest_framework.views import APIView

from stores.models import Store

from . import llm as llm_module
from .models import AgentRunStatus
from .services import DuplicateRun, run_agent


class ChatRequestSerializer(serializers.Serializer):
    message = serializers.CharField(max_length=1000)


class ChatView(APIView):
    """POST /api/stores/<slug>/chat  {"message": "..."}  + header Idempotency-Key.

    Public on purpose: shoppers are not Django users. That makes it the one
    explicit exception to deny-by-default, so it MUST be throttled: every
    request here spends LLM money (E3).
    """

    authentication_classes = []  # no session -> no CSRF; shoppers aren't logged in
    permission_classes = [AllowAny]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "chat"

    def post(self, request, store_slug):
        store = get_object_or_404(Store, slug=store_slug)

        key = request.headers.get("Idempotency-Key", "").strip()
        if not key or len(key) > 100:
            return Response(
                {"error": "Send an Idempotency-Key header (1-100 chars), new for each message."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        body = ChatRequestSerializer(data=request.data)
        body.is_valid(raise_exception=True)

        try:
            result = run_agent(store, body.validated_data["message"], key, llm_module.build_llm())
        except DuplicateRun as dup:
            return Response(
                {"error": "This message was already sent.", "run_id": str(dup.run.id)},
                status=status.HTTP_409_CONFLICT,
            )

        if result.run.status != AgentRunStatus.SUCCEEDED:
            # The details are in the LLMCall rows; the shopper gets a calm message.
            return Response(
                {"error": "The assistant is unavailable right now. Please try again.",
                 "run_id": str(result.run.id)},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )

        return Response({"answer": result.answer, "run_id": str(result.run.id)})
