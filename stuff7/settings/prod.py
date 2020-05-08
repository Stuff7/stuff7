import os
from .base import env

host = "http://localhost"

ALLOWED_HOSTS = ["localhost", "127.0.0.1"]

DATABASES = {
  "default": {
    "ENGINE": "django.db.backends.mysql",
    "NAME": env("DB_NAME"),
    "USER": env("DB_USER"),
    "PASSWORD": env("DB_PASSWORD"),
    "HOST": env("DB_HOST"),
    "PORT": env("DB_PORT"),
    "TEST_CHARSET": "utf8",
    "TEST_COLLATION": "utf8_general_ci",
  }
}
