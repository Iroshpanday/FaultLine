"""Ask the real agent one question, end to end, and show what it logged.

    python manage.py ask_agent momo-mart "Where is my order #123?"

Uses the real LLM (2 requests of your free quota per order question).
"""

import uuid

from django.core.management.base import BaseCommand, CommandError

from agent.llm import build_llm
from agent.services import run_agent
from stores.models import Store


class Command(BaseCommand):
    help = "Ask the real agent one question for a store and print the answer and its LLM calls."

    def add_arguments(self, parser):
        parser.add_argument("store_slug")
        parser.add_argument("question")

    def handle(self, *args, store_slug, question, **options):
        store = Store.objects.filter(slug=store_slug).first()
        if store is None:
            raise CommandError(f"No store with slug {store_slug!r}. Run: python manage.py seed_demo")
        try:
            llm = build_llm()
        except ValueError as exc:
            raise CommandError(f"{exc}. Add it to backend/.env.") from None

        # A fresh key per command run: each run is a new question.
        result = run_agent(store, question, f"cli-{uuid.uuid4()}", llm)
        run = result.run

        self.stdout.write(f"store:   {store.name}")
        self.stdout.write(f"answer:  {result.answer}")
        self.stdout.write(f"run:     {run.id}  status={run.status}  steps={run.steps}")
        for call in run.llm_calls.order_by("attempt_number"):
            self.stdout.write(
                f"  call #{call.attempt_number}: {call.status:<9} {call.error_category or '':<14}"
                f" {call.latency_ms} ms  tokens in={call.input_tokens} out={call.output_tokens}"
                f"  cost={_money(call.cost)} ({call.cost_source})"
            )


def _money(value):
    # Decimal("0E-8") is how Python shows 0 stored with 8 decimal places.
    return "unknown" if value is None else f"{value:f}"
