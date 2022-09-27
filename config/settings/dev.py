from .base import *  # pylint: disable=wildcard-import,unused-wildcard-import


# Django settings
# ---------------
SECRET_KEY = "foobar"

DEBUG = True

ALLOWED_HOSTS = ["localhost", "0.0.0.0", "127.0.0.1", "192.168.0.1"]

# Security.
# ------------------------------------------------------------------------------
SESSION_COOKIE_SECURE = False

CSRF_COOKIE_SECURE = False

AUTH_PASSWORD_VALIDATORS = []  # Avoid password strength validation in DEV.

# Database
# https://docs.djangoproject.com/en/4.1/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql_psycopg2",
        "HOST": os.getenv("POSTGRESQL_ADDON_HOST"),
        "PORT": os.getenv("POSTGRES_PORT"),
        "NAME": os.getenv("POSTGRESQL_ADDON_DB"),
        "USER": os.getenv("POSTGRES_USER"),
        "PASSWORD": os.getenv("POSTGRES_PASSWORD"),
    }
}
