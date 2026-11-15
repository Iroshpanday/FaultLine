from django.conf import settings

from .base import LLMAdapter
from .openrouter import OpenRouterLLM


def build_llm() -> LLMAdapter:
    """The real LLM configured in settings. Tests replace this with FakeLLM."""
    return OpenRouterLLM(
        settings.OPENROUTER_API_KEY,
        settings.OPENROUTER_MODEL,
        settings.OPENROUTER_TIMEOUT_SECONDS,
    )
