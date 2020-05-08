import os

from .base import root

host = "http://localhost"

# This allows us to use a plain HTTP callback in OAuth flow.
os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

ALLOWED_HOSTS = ["localhost", "192.168.1.91"]

# Database
# https://docs.djangoproject.com/en/3.0/ref/settings/#databases
DATABASES = {
  "default": {
    "ENGINE": "django.db.backends.sqlite3",
    "NAME": root("db.sqlite3"),
  }
}
