"""Send ONE real request to the configured LLM and print what came back.

    python manage.py llm_ping           # plain text question
    python manage.py llm_ping --tool    # check the model can call a tool

Uses your real key and counts against your free daily limit. Never prints the key.
"""

import time

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from agent.llm.base import ProviderError
from agent.llm.openrouter import OpenRouterLLM

ORDER_TOOL = {
    "type": "function",
    "function": {
        "name": "get_order_status",
        "description": "Look up the status of a customer's order by its number.",
        "parameters": {
            "type": "object",
            "properties": {"order_number": {"type": "integer"}},
            "required": ["order_number"],
        },
    },
}


class Command(BaseCommand):
    help = "Send one real request to the configured LLM (costs one request of your quota)."

    def add_arguments(self, parser):
        parser.add_argument("--tool", action="store_true", help="Offer get_order_status and ask about an order.")

    def handle(self, *args, **options):
        try:
            llm = OpenRouterLLM(
                settings.OPENROUTER_API_KEY,
                settings.OPENROUTER_MODEL,
                settings.OPENROUTER_TIMEOUT_SECONDS,
            )
        except ValueError as exc:
            raise CommandError(f"{exc}. Add it to backend/.env.") from None

        if options["tool"]:
            messages = [{"role": "user", "content": "Where is my order #123?"}]
            tools = [ORDER_TOOL]
        else:
            messages = [{"role": "user", "content": "Say hello in one short sentence."}]
            tools = None

        self.stdout.write(f"model: {llm.model}")
        started = time.monotonic()
        try:
            resp = llm.complete(messages, tools=tools)
        except ProviderError as exc:
            raise CommandError(f"{type(exc).__name__}: {exc}") from None
        latency_ms = round((time.monotonic() - started) * 1000)

        self.stdout.write(f"text:        {resp.text!r}")
        for call in resp.tool_calls:
            self.stdout.write(f"tool call:   {call.name}({call.arguments}) id={call.id}")
        usage = resp.usage
        self.stdout.write(f"tokens:      in={usage.input_tokens if usage else None} out={usage.output_tokens if usage else None}")
        self.stdout.write(f"cost:        {resp.cost} USD")
        self.stdout.write(f"latency:     {latency_ms} ms")
        self.stdout.write(f"request id:  {resp.provider_request_id}")
