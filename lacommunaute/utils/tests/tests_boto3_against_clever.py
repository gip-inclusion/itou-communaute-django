import os

import botocore
import pytest

from lacommunaute.forum.factories import ForumFactory
from lacommunaute.forum.models import Forum


# CleverCloud S3 implementation does not support recent data integrity features from AWS.
# https://github.com/boto/boto3/issues/4392
# https://github.com/boto/boto3/issues/4398#issuecomment-2619946229
#
# This test is here to ensure that we are not using a boto3 version that is too recent.
# If the test fails, it means that we can update the boto3 version in the requirements.txt to newer versions.
#
def test_boto3_lib_version_against_clever(db):
    if os.getenv("CELLAR_ADDON_KEY_ID"):
        with pytest.raises(botocore.exceptions.ClientError):
            ForumFactory(with_image=True)
    else:
        ForumFactory(with_image=True)
        assert Forum.objects.exists()
