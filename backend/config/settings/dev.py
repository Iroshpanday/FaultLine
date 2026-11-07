from .base import *  # noqa: F403
from .base import env

SECRET_KEY = env("DJANGO_SECRET_KEY", default="dev-only-insecure-key-never-use-in-prod")
DEBUG = True
ALLOWED_HOSTS = ["localhost", "127.0.0.1"]

STORE_PROMPTS = env.bool("STORE_PROMPTS", default=True)
