import pytest
from django.db import IntegrityError

from agent.factories import AgentRunFactory, LLMCallFactory

pytestmark = pytest.mark.django_db


def test_failed_call_without_error_category_is_rejected():
    # The factory default is error_category="", so a failed call says nothing about why.
    with pytest.raises(IntegrityError):
        LLMCallFactory(status="failed")


def test_same_attempt_number_twice_in_one_run_is_rejected():
    run = AgentRunFactory()
    LLMCallFactory(agent_run=run, attempt_number=1)

    with pytest.raises(IntegrityError):
        LLMCallFactory(agent_run=run, attempt_number=1)
