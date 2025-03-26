import os

import boto3
import pytest
from botocore.config import Config
from django.conf import settings

from lacommunaute.forum.factories import ForumFactory
from lacommunaute.forum.models import Forum


# CleverCloud S3 implementation does not support recent data integrity features from AWS.
# https://github.com/boto/boto3/issues/4392
# https://github.com/boto/boto3/issues/4398#issuecomment-2619946229
#
# This test is here to ensure that file operations are ok on live cellar, to prevent
# future failure.
#
@pytest.mark.skipif(os.getenv("CELLAR_ADDON_KEY_ID") is None, reason="Not using Cellar")
def test_e2e_file_can_be_uploaded_to_cellar(db):
    ForumFactory(with_image=True)
    assert Forum.objects.exists()


#
# This test is expected not fail when live cellar conf will accept the integrity protection.
# At that time, `Config()` in `base.py` should be clean up.
#
@pytest.mark.skipif(os.getenv("CELLAR_ADDON_KEY_ID") is None, reason="Not using Cellar")
@pytest.mark.xfail
def test_cellar_does_not_support_checksum_validation():
    client = boto3.client(
        "s3",
        endpoint_url=settings.AWS_S3_ENDPOINT_URL,
        aws_access_key_id=settings.AWS_S3_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_S3_SECRET_ACCESS_KEY,
        region_name=settings.AWS_S3_STORAGE_BUCKET_REGION,
        config=Config(),
    )
    client.put_object(Bucket=settings.AWS_STORAGE_BUCKET_NAME, Body=b"", Key="file")
