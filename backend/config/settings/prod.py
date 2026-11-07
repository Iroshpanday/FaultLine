from .base import *  # noqa: F403
from .base import env

DEBUG = False
# Required, no default: prod must never run with a key that is in the repo.
SECRET_KEY = env("DJANGO_SECRET_KEY")
# Required: a missing value crashes at startup instead of serving with a bad config.
ALLOWED_HOSTS = env.list("DJANGO_ALLOWED_HOSTS")

SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = 60 * 60 * 24 * 30
SECURE_CONTENT_TYPE_NOSNIFF = True

# Reuse DB connections across requests; health checks drop dead ones first.
# These are per-database keys: as top-level settings Django silently ignores them.
DATABASES["default"]["CONN_MAX_AGE"] = 60  # noqa: F405
DATABASES["default"]["CONN_HEALTH_CHECKS"] = True  # noqa: F405
