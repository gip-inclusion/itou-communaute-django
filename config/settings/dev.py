# Enable django-debug-toolbar with Docker.
import socket

from lacommunaute.utils.enums import Environment

from .test import *  # pylint: disable=wildcard-import,unused-wildcard-import # noqa: F403 F401


# Django settings
# ---------------
DEBUG = True
ENVIRONMENT = Environment.DEV

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

# See: https://docs.djangoproject.com/en/dev/ref/settings/#media-url
MEDIA_URL = f"{AWS_S3_ENDPOINT_URL}/"  # noqa: F405

CONTENT_SECURITY_POLICY["DIRECTIVES"]["default-src"] = ["*"]  # noqa undefined-local-with-import-star-usage
CONTENT_SECURITY_POLICY["DIRECTIVES"]["img-src"].append("localhost:9000")  # noqa undefined-local-with-import-star-usage

COMMU_PROTOCOL = "http"
COMMU_FQDN = "127.0.0.1:8000"
