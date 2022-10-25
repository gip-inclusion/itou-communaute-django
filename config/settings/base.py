import os

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

ALLOWED_HOSTS = os.getenv(
    "ALLOWED_HOSTS", "inclusion.beta.gouv.fr,communaute.inclusion.beta.gouv.fr"
).split(",")

# Application definition
DJANGO_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.postgres",
]

THIRD_PARTIES_APPS = [
    # Django Storage for S3
    "storages",
    # Machina dependencies:
    "mptt",  # to handle the tree of forum instances
    "haystack",  # search capabilities
    "widget_tweaks",
    # Machina apps:
    "machina",
    "machina.apps.forum_feeds",
    "machina.apps.forum_moderation",
    "machina.apps.forum_search",
    "machina.apps.forum_tracking",
    "machina.apps.forum_permission",
    # django-compressor
    "compressor",
]

# MIGRATION CONFIGURATION
# ------------------------------------------------------------------------------

MIGRATION_MODULES = {
    "forum_member": "machina.apps.forum_member.migrations",
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
    "lacommunaute.inclusion_connect",
    "lacommunaute.www",
]

INSTALLED_APPS = DJANGO_APPS + LOCAL_APPS + THIRD_PARTIES_APPS

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "machina.apps.forum_permission.middleware.ForumPermissionMiddleware",
]

ROOT_URLCONF = "config.urls"
LOGIN_REDIRECT_URL = "/forum"
LOGOUT_REDIRECT_URL = "/forum"

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

# Internationalization
# https://docs.djangoproject.com/en/4.1/topics/i18n/

LANGUAGE_CODE = "fr-FR"
USE_I18N = True
USE_L10N = True
LOCALE_PATHS = (os.path.join(ROOT_DIR, "locale"),)

TIME_ZONE = "Europe/Paris"
USE_TZ = True
DATE_INPUT_FORMATS = ["%d/%m/%Y", "%d-%m-%Y", "%d %m %Y"]


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.1/howto/static-files/
STATIC_ROOT = os.path.join(ROOT_DIR, "public/static")

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

COMPRESS_PRECOMPILERS = (
    ('text/x-scss', 'django_libsass.SassCompiler'),
)

# Default primary key field type
# https://docs.djangoproject.com/en/4.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Cache
# TODO : improve default cache later, with pymemcache or redis
# https://docs.djangoproject.com/en/4.1/topics/cache/
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
    },
    "machina_attachments": {
        "BACKEND": "django.core.cache.backends.filebased.FileBasedCache",
        "LOCATION": "/tmp",
    },
}

# Search Backend
# TODO : improve it later with woosh or elastic search
HAYSTACK_CONNECTIONS = {
    "default": {
        "ENGINE": "haystack.backends.simple_backend.SimpleEngine",
    },
}

# Environment, sets the type of env of the app (PROD, DEV…)
ITOU_ENVIRONMENT = os.getenv("ITOU_ENVIRONMENT", "PROD")
ITOU_PROTOCOL = "https"
ITOU_FQDN = os.getenv("ITOU_FQDN", "communaute-experimentation.inclusion.beta.gouv.fr")

# S3 uploads
# ------------------------------------------------------------------------------

AWS_S3_ACCESS_KEY_ID = os.getenv("CELLAR_ADDON_KEY_ID", "123")
AWS_S3_SECRET_ACCESS_KEY = os.getenv("CELLAR_ADDON_KEY_SECRET", "secret")
AWS_S3_ENDPOINT_URL = os.getenv("CELLAR_ADDON_HOST", "http://set-var-env.com/")
AWS_STORAGE_BUCKET_NAME = os.getenv("S3_STORAGE_BUCKET_NAME", "set-bucket-name")
AWS_S3_STORAGE_BUCKET_REGION = os.getenv("S3_STORAGE_BUCKET_REGION", "fr")

# MEDIA CONFIGURATION
# ------------------------------------------------------------------------------

# See: https://docs.djangoproject.com/en/dev/ref/settings/#media-root
MEDIA_ROOT = os.path.join(APPS_DIR, "media")

# See: https://docs.djangoproject.com/en/dev/ref/settings/#media-url
MEDIA_URL = f"https://{AWS_S3_ENDPOINT_URL}/"  # noqa

DEFAULT_FILE_STORAGE = "storages.backends.s3boto3.S3Boto3Storage"
MACHINA_FORUM_NAME = "La Communauté"
FORUM_TOPICS_NUMBER_PER_PAGE = 10

# Inclusion Connect
INCLUSION_CONNECT_BASE_URL = os.getenv("INCLUSION_CONNECT_BASE_URL")
INCLUSION_CONNECT_REALM = os.getenv("INCLUSION_CONNECT_REALM")
INCLUSION_CONNECT_CLIENT_ID = os.getenv("INCLUSION_CONNECT_CLIENT_ID")
INCLUSION_CONNECT_CLIENT_SECRET = os.getenv("INCLUSION_CONNECT_CLIENT_SECRET")
