import os

from lacommunaute.utils.enums import Environment

from .base import *  # pylint: disable=wildcard-import,unused-wildcard-import # noqa: F403 F401


# Django settings
# ---------------
SECRET_KEY = "v3ry_s3cr3t_k3y"

ENVIRONMENT = Environment.TEST

# Database
# ------------------------------------------------------------------------------
DATABASES["default"]["HOST"] = os.getenv("PGHOST", "localhost")  # noqa: F405
DATABASES["default"]["PORT"] = os.getenv("PGPORT", "5432")  # noqa: F405
DATABASES["default"]["NAME"] = os.getenv("PGDATABASE", "communaute")  # noqa: F405
DATABASES["default"]["USER"] = os.getenv("PGUSER", "postgres")  # noqa: F405
DATABASES["default"]["PASSWORD"] = os.getenv("PGPASSWORD", "password")  # noqa: F405

# S3 uploads
# ------------------------------------------------------------------------------

AWS_S3_ACCESS_KEY_ID = os.getenv("CELLAR_ADDON_KEY_ID", "minioadmin")
AWS_S3_SECRET_ACCESS_KEY = os.getenv("CELLAR_ADDON_KEY_SECRET", "minioadmin")
AWS_S3_ENDPOINT_URL = (
    f"{os.getenv('CELLAR_ADDON_PROTOCOL', 'http')}://{os.getenv('CELLAR_ADDON_HOST', 'localhost:9000')}"
)
AWS_STORAGE_BUCKET_NAME = "c3-django-review-bucket"
AWS_STORAGE_BUCKET_NAME_PUBLIC = "c3-django-review-bucket-public"
AWS_S3_STORAGE_BUCKET_REGION = "eu-west-3"

MEDIA_URL = f"{AWS_S3_ENDPOINT_URL}/"

# SENDINBLUE
# ---------------------------------------
SIB_URL = "http://test.com"
SIB_API_KEY = "dummy-sib-api-key"

# EMPLOIS
# ---------------------------------------
EMPLOIS_PRESCRIBER_SEARCH = "http://test.com/prescriber/search"
EMPLOIS_COMPANY_SEARCH = "http://test.com/company/search"

EMAIL_LAST_SEEN_HASH_SALT = "bobby"

# Nexus metabase db
# ---------------------------------------
NEXUS_METABASE_DB_HOST = DATABASES["default"]["HOST"]
NEXUS_METABASE_DB_PORT = DATABASES["default"]["PORT"]
NEXUS_METABASE_DB_DATABASE = DATABASES["default"]["NAME"]
NEXUS_METABASE_DB_USER = DATABASES["default"]["USER"]
NEXUS_METABASE_DB_PASSWORD = DATABASES["default"]["PASSWORD"]
