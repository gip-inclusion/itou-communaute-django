import os

import csp.constants
from botocore.config import Config
from dotenv import load_dotenv
from machina import MACHINA_MAIN_STATIC_DIR, MACHINA_MAIN_TEMPLATE_DIR


load_dotenv()

# Django settings
# See https://docs.djangoproject.com/en/4.1/howto/deployment/checklist/
# ---------------
_current_dir = os.path.dirname(os.path.realpath(__file__))
ROOT_DIR = os.path.abspath(os.path.join(_current_dir, "../.."))

APPS_DIR = os.path.abspath(os.path.join(ROOT_DIR, "lacommunaute"))

SECRET_KEY = os.getenv("DJANGO_SECRET_KEY")

DEBUG = os.getenv("DJANGO_DEBUG", "False") == "True"
ENVIRONMENT = os.getenv("ENVIRONMENT")

PARKING_PAGE = os.getenv("PARKING_PAGE", "False") == "True"

ALLOWED_HOSTS = os.getenv("ALLOWED_HOSTS", "communaute.inclusion.gouv.fr,").split(",")

# Application definition
DJANGO_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.postgres",
    "django.contrib.sites",
    "django.contrib.sitemaps",
    "django.contrib.redirects",
    "django.contrib.flatpages",
]

THIRD_PARTIES_APPS = [
    # Django Storage for S3
    "storages",
    # Machina dependencies:
    "haystack",  # Provides search, but is unused.
    "mptt",  # to handle the tree of forum instances
    "widget_tweaks",
    # Machina apps:
    "machina",
    "machina.apps.forum_tracking",
    # django-compressor
    "compressor",
    "django_social_share",
    "django_htmx",
    "taggit",
    "csp",
]

# MIGRATION CONFIGURATION
# ------------------------------------------------------------------------------

MIGRATION_MODULES = {
    "forum_member": "lacommunaute.forum_member.migrations",
    "forum_tracking": "lacommunaute.forum_tracking.migrations",
    "forum_permission": "lacommunaute.forum_permission.migrations",
}

LOCAL_APPS = [
    # Core apps, order is important.
    "lacommunaute.users",
    "lacommunaute.utils",
    "lacommunaute.forum",
    "lacommunaute.forum_conversation",
    "lacommunaute.forum_conversation.forum_attachments",
    "lacommunaute.forum_conversation.forum_polls",
    "lacommunaute.forum_member",
    "lacommunaute.forum_upvote",
    "lacommunaute.stats",
    "lacommunaute.forum_moderation",
    "lacommunaute.forum_permission",
    "lacommunaute.notification",
    "lacommunaute.event",
    "lacommunaute.openid_connect",
    "lacommunaute.pages",
    "lacommunaute.forum_file",
    "lacommunaute.search",
    "lacommunaute.surveys",
    "lacommunaute.partner",
]

INSTALLED_APPS = DJANGO_APPS + LOCAL_APPS + THIRD_PARTIES_APPS

DJANGO_MIDDLEWARE = [
    "django.middleware.gzip.GZipMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.redirects.middleware.RedirectFallbackMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "lacommunaute.utils.middleware.ParkingPageMiddleware",
    "lacommunaute.openid_connect.middleware.ProConnectLoginMiddleware",
    "lacommunaute.notification.middleware.NotificationMiddleware",
    "lacommunaute.users.middleware.MarkAsSeenLoggedUserMiddleware",
]

THIRD_PARTIES_MIDDLEWARE = [
    "csp.middleware.CSPMiddleware",
    "django_permissions_policy.PermissionsPolicyMiddleware",
    "django_htmx.middleware.HtmxMiddleware",
]

LOCAL_MIDDLEWARE = [
    "machina.apps.forum_permission.middleware.ForumPermissionMiddleware",
]

MIDDLEWARE = DJANGO_MIDDLEWARE + THIRD_PARTIES_MIDDLEWARE + LOCAL_MIDDLEWARE

ROOT_URLCONF = "config.urls"
LOGIN_URL = "/users/login/"
LOGIN_REDIRECT_URL = "/"
LOGOUT_REDIRECT_URL = "/"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [
            os.path.join(APPS_DIR, "templates"),
            MACHINA_MAIN_TEMPLATE_DIR,
        ],
        # "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.template.context_processors.media",
                "django.contrib.messages.context_processors.messages",
                "machina.core.context_processors.metadata",
                "lacommunaute.utils.settings_context_processors.expose_settings",
            ],
            "loaders": [
                "django.template.loaders.filesystem.Loader",
                "django.template.loaders.app_directories.Loader",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"


# Database
# https://docs.djangoproject.com/en/4.1/ref/settings/#databases

DATABASES = {
    "default": {
        "ATOMIC_REQUESTS": True,
        "ENGINE": "django.db.backends.postgresql_psycopg2",
        "HOST": os.getenv("POSTGRESQL_ADDON_HOST"),
        "PORT": os.getenv("POSTGRESQL_ADDON_PORT"),
        "NAME": os.getenv("POSTGRESQL_ADDON_DB"),
        "USER": os.getenv("POSTGRESQL_ADDON_USER"),
        "PASSWORD": os.getenv("POSTGRESQL_ADDON_PASSWORD"),
    }
}


# Password validation
# https://docs.djangoproject.com/en/4.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

# Auth.
# ------------------------------------------------------------------------------
AUTH_USER_MODEL = "users.User"

AUTHENTICATION_BACKENDS = (
    # Needed to login by username in Django admin.
    "django.contrib.auth.backends.ModelBackend",
)

# TODO: Remove with Django 6.0
FORMS_URLFIELD_ASSUME_HTTPS = True

# Internationalization
# https://docs.djangoproject.com/en/4.1/topics/i18n/

LANGUAGE_CODE = "fr-FR"
USE_I18N = True
LOCALE_PATHS = (os.path.join(ROOT_DIR, "locale"),)

TIME_ZONE = "Europe/Paris"
USE_TZ = True
DATE_INPUT_FORMATS = ["%d/%m/%Y", "%d-%m-%Y", "%d %m %Y"]

# STORAGE (django >= 4.2)
STORAGES = {
    "default": {"BACKEND": "storages.backends.s3boto3.S3Boto3Storage"},
    "staticfiles": {"BACKEND": "django.contrib.staticfiles.storage.ManifestStaticFilesStorage"},
}

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.1/howto/static-files/

# Static Files
STATIC_URL = "/static/"

STATICFILES_DIRS = [
    os.path.join(APPS_DIR, "static"),
    MACHINA_MAIN_STATIC_DIR,
]

STATIC_ROOT = os.path.join(APPS_DIR, "staticfiles")

STATICFILES_FINDERS = [
    "django.contrib.staticfiles.finders.FileSystemFinder",
    "django.contrib.staticfiles.finders.AppDirectoriesFinder",
    "compressor.finders.CompressorFinder",
]

COMPRESS_PRECOMPILERS = (("text/x-scss", "django_libsass.SassCompiler"),)
COMPRESS_OFFLINE = True
COMPRESS_OFFLINE_CONTEXT = {
    "BASE_TEMPLATE": "layouts/base.html",
    # Do not import machina settings for that value. It forces evaluation
    # of machina’s getattr(settings, "XXX", MACHINA_DEFAULT) before our
    # settings have be defined, thus preventing our overrides.
    "MACHINA_BASE_TEMPLATE_NAME": "_base.html",
}

# Default primary key field type
# https://docs.djangoproject.com/en/4.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Cache
# TODO : improve default cache later, with pymemcache or redis
# https://docs.djangoproject.com/en/4.1/topics/cache/
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.db.DatabaseCache",
        "LOCATION": "cache_table",
    },
    "machina_attachments": {
        "BACKEND": "django.core.cache.backends.filebased.FileBasedCache",
        "LOCATION": "/tmp",
    },
}

COMMU_PROTOCOL = "https"
COMMU_FQDN = os.getenv("COMMU_FQDN", "communaute.inclusion.gouv.fr")

# S3 uploads
# ------------------------------------------------------------------------------

AWS_S3_ACCESS_KEY_ID = os.getenv("CELLAR_ADDON_KEY_ID")
AWS_S3_SECRET_ACCESS_KEY = os.getenv("CELLAR_ADDON_KEY_SECRET")
AWS_S3_ENDPOINT_URL = f"{os.getenv('CELLAR_ADDON_PROTOCOL', 'https')}://{os.getenv('CELLAR_ADDON_HOST')}"
AWS_STORAGE_BUCKET_NAME = os.getenv("S3_STORAGE_BUCKET_NAME")
AWS_STORAGE_BUCKET_NAME_PUBLIC = os.getenv("S3_STORAGE_BUCKET_NAME_PUBLIC")
AWS_S3_STORAGE_BUCKET_REGION = os.getenv("S3_STORAGE_BUCKET_REGION")
# CleverCloud S3 implementation does not support recent data integrity features from AWS.
# https://github.com/boto/boto3/issues/4392
# https://github.com/boto/boto3/issues/4398#issuecomment-2619946229
AWS_S3_CLIENT_CONFIG = Config(
    request_checksum_calculation="when_required",
    response_checksum_validation="when_required",
)

# MEDIA CONFIGURATION
# ------------------------------------------------------------------------------

# See: https://docs.djangoproject.com/en/dev/ref/settings/#media-root
MEDIA_ROOT = os.path.join(APPS_DIR, "media")

# See: https://docs.djangoproject.com/en/dev/ref/settings/#media-url
MEDIA_URL = f"{AWS_S3_ENDPOINT_URL}/"  # noqa

# Forum - Machina settings
# ------------------------------------------------------------------------------
MACHINA_FORUM_NAME = "La communauté de l'inclusion"
FORUM_TOPICS_NUMBER_PER_PAGE = 10
FORUM_NUMBER_POSTS_PER_TOPIC = 5
MACHINA_FORUM_IMAGE_WIDTH = 300
MACHINA_FORUM_IMAGE_HEIGHT = 300

# Actually unused, but required by Machina.
HAYSTACK_CONNECTIONS = {
    "default": {
        "ENGINE": "haystack.backends.simple_backend.SimpleEngine",
    },
}

# Inclusion Connect
# ------------------------------------------------------------------------------
OPENID_CONNECT_BASE_URL = os.getenv("OPENID_CONNECT_BASE_URL")
OPENID_CONNECT_CLIENT_ID = os.getenv("OPENID_CONNECT_CLIENT_ID")
OPENID_CONNECT_CLIENT_SECRET = os.getenv("OPENID_CONNECT_CLIENT_SECRET")

# LOGGING
# ------------------------------------------------------------------------------
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "simple": {
            "format": "{levelname} {asctime} {pathname} : {message}",
            "style": "{",
        },
    },
    "handlers": {
        "console": {"class": "logging.StreamHandler", "formatter": "simple"},
    },
    "loggers": {
        "django": {
            "handlers": ["console"],
            "level": os.getenv("DJANGO_LOG_LEVEL", "INFO"),
        },
        "commands": {
            "handlers": ["console"],
            "level": os.getenv("COMMANDS_LOG_LEVEL", "INFO"),
        },
    },
}

_sentry_dsn = os.getenv("SENTRY_DSN")
if _sentry_dsn:
    from ._sentry import sentry_init

    sentry_init(dsn=_sentry_dsn)

# WIDGETS
# ---------------------------------------
MACHINA_MARKUP_WIDGET = "lacommunaute.forum_conversation.widgets.MarkdownTextareaWidget"
MACHINA_MARKUP_LANGUAGE = (
    "machina.core.markdown.markdown",
    {"safe_mode": False, "extras": {"break-on-newline": True, "code-friendly": True, "nofollow": True}},
)
SUPPORTED_IMAGE_FILE_TYPES = {"image/png": "png", "image/jpeg": "jpeg", "image/jpg": "jpg", "image/gif": "gif"}

# Django sites framework
SITE_ID = 1

DSP_FORUM_RELATED_ID = 108
STAFF_GROUP_NAME = "Equipe"

API_BAN_BASE_URL = "https://api-adresse.data.gouv.fr"

# EMPLOI
# ------------------------------------------------------------------------------
EMPLOI_BASE_URL = os.getenv("EMPLOI_BASE_URL", "https://emplois.inclusion.beta.gouv.fr")
EMPLOIS_PRESCRIBER_SEARCH = f"{EMPLOI_BASE_URL}/search/prescribers"
EMPLOIS_COMPANY_SEARCH = f"{EMPLOI_BASE_URL}/search/employers"

# MATOMO
# ---------------------------------------
MATOMO_BASE_URL = os.getenv("MATOMO_BASE_URL", None)
MATOMO_SITE_ID = int(os.getenv("MATOMO_SITE_ID", "1"))
MATOMO_AUTH_TOKEN = os.getenv("MATOMO_AUTH_TOKEN", None)

# SENDINBLUE
# ---------------------------------------
SIB_URL = os.getenv("SIB_URL")
SIB_SMTP_ROUTE = "smtp/email"
SIB_CONTACTS_ROUTE = "contacts/import"

SIB_API_KEY = os.getenv("SIB_API_KEY")
DEFAULT_FROM_EMAIL = os.getenv("DEFAULT_FROM_EMAIL", "noreply@inclusion.gouv.fr")

SIB_MAGIC_LINK_TEMPLATE = 31
SIB_UNANSWERED_QUESTION_TEMPLATE = 10
SIB_ONBOARDING_LIST = 5
SIB_NEW_MESSAGES_TEMPLATE = 28
SIB_MISSYOU_TEMPLATE = 40
NEW_MESSAGES_EMAIL_MAX_PREVIEW = 10

# TAGGIT
# ---------------------------------------
TAGGIT_CASE_INSENSITIVE = True
TAGGIT_STRIP_UNICODE_WHEN_SLUGIFY = True

# CSP
# ---------------------------------------
connect_src = [
    csp.constants.SELF,
    "*.sentry.io",
]
img_src = [
    csp.constants.SELF,
    "data:",
    "cellar-c2.services.clever-cloud.com",
]
script_src = [
    csp.constants.SELF,
    csp.constants.NONCE,
    "https://cdn.jsdelivr.net/npm/chart.js@4.0.1",
    "https://cdn.jsdelivr.net/npm/jquery@3.6.1/dist/jquery.min.js",
    "https://cdn.jsdelivr.net/npm/@popperjs/core@2.11.8/dist/umd/popper.min.js",
    "https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.min.js",
    # https://docs.sentry.io/platforms/javascript/install/loader/#content-security-policy
    "https://browser.sentry-cdn.com/9.30.0/bundle.min.js",
    "https://tally.so",
    "https://www.youtube.com/iframe_api",
    "https://www.youtube.com/s/player/",
]
style_src = [
    csp.constants.SELF,
    "https://fonts.googleapis.com",
    csp.constants.UNSAFE_INLINE,  # needed for htmx.js, embed.js & tartecitron.js
]
if API_BAN_BASE_URL:
    connect_src += [
        API_BAN_BASE_URL,
    ]

if MATOMO_BASE_URL:
    connect_src += [
        MATOMO_BASE_URL,
    ]
    img_src += [
        MATOMO_BASE_URL,
    ]
    script_src += [
        MATOMO_BASE_URL,
    ]

CONTENT_SECURITY_POLICY = {
    "DIRECTIVES": {
        "default-src": [
            csp.constants.SELF,
        ],
        "connect-src": connect_src,
        "img-src": img_src,
        "frame-src": [
            csp.constants.SELF,
            "https://tally.so",
            "https://www.youtube.com/embed/",
        ],
        "font-src": [
            csp.constants.SELF,
            "https://fonts.gstatic.com/",
            "data:",
        ],
        "script-src": script_src,
        "script-src-elem": script_src,
        "style-src": style_src,
        "style-src-elem": style_src,
    },
}

# HSTS
# ---------------------------------------
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# Clickjacking
# ---------------------------------------
X_FRAME_OPTIONS = "DENY"

# SECURITY
# ---------------------------------------
# See https://docs.djangoproject.com/en/4.1/topics/security/
# and https://docs.djangoproject.com/en/4.1/ref/middleware/#module-django.middleware.security
# See https://docs.djangoproject.com/en/4.1/ref/middleware/#http-strict-transport-security

SECURE_CONTENT_TYPE_NOSNIFF = True

SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

SECURE_CROSS_ORIGIN_OPENER_POLICY = "same-origin"

# SESSIONS
# ---------------------------------------
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

# PERMISSIONS POLICIES
# ---------------------------------------
PERMISSIONS_POLICY = {
    "accelerometer": [],
    "autoplay": [],
    "camera": [],
    "encrypted-media": [],
    "fullscreen": [],
    "geolocation": [],
    "gyroscope": [],
    "magnetometer": [],
    "microphone": [],
    "midi": [],
    "payment": [],
    "picture-in-picture": [],
    "sync-xhr": [],
    "usb": [],
}

# ARCHIVE OLD PERSONNAL DATAS
# ---------------------------------------
EMAIL_LAST_SEEN_HASH_SALT = os.getenv("EMAIL_LAST_SEEN_HASH_SALT")
EMAIL_LAST_SEEN_MISSYOU_BATCH_SIZE = 25
EMAIL_LAST_SEEN_ARCHIVE_PERSONNAL_DATAS_DELAY = 30  # days
EMAIL_LAST_SEEN_MISSYOU_DELAY = 2 * 365 - EMAIL_LAST_SEEN_ARCHIVE_PERSONNAL_DATAS_DELAY  # days
