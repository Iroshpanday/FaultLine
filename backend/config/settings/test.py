from .base import *  # noqa: F403

# pytest-django creates a separate "test_<POSTGRES_DB>" database on the same
# server, so the DB user needs CREATEDB. Same engine as prod, never SQLite.

SECRET_KEY = "test-only-insecure-key"

# Hashing passwords with PBKDF2 makes every user factory slow; tests don't need it.
PASSWORD_HASHERS = ["django.contrib.auth.hashers.MD5PasswordHasher"]

# Tests decide prompt storage explicitly (override_settings), never via the environment.
STORE_PROMPTS = False

# Tests never reach a real provider: with no key, the OpenRouter adapter
# refuses to be built, so a test that forgets FakeLLM fails loudly.
OPENROUTER_API_KEY = ""
