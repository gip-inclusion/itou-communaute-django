import os

from .base import *  # pylint: disable=wildcard-import,unused-wildcard-import # noqa: F403 F401


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

# Django-extensions.
# ------------------------------------------------------------------------------

INSTALLED_APPS += ["django_extensions"]  # noqa F405

# Django-debug-toolbar.
# ------------------------------------------------------------------------------

INSTALLED_APPS += ["debug_toolbar"]  # noqa F405

INTERNAL_IPS = ["127.0.0.1"]

# Enable django-debug-toolbar with Docker.
import socket


_, _, ips = socket.gethostbyname_ex(socket.gethostname())
INTERNAL_IPS += [ip[:-1] + "1" for ip in ips]

MIDDLEWARE += ["debug_toolbar.middleware.DebugToolbarMiddleware"]  # noqa F405

DEBUG_TOOLBAR_CONFIG = {
    # https://django-debug-toolbar.readthedocs.io/en/latest/panels.html#panels
    "DISABLE_PANELS": [
        "debug_toolbar.panels.redirects.RedirectsPanel",
        # ProfilingPanel makes the django admin extremely slow...
        "debug_toolbar.panels.profiling.ProfilingPanel",
    ],
    "SHOW_TEMPLATE_CONTEXT": True,
}

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
