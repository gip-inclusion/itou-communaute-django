import os
from io import BytesIO

import boto3
import faker
import pytest
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from moto import mock_aws
from PIL import Image

from lacommunaute.forum_file.models import PublicFile
from lacommunaute.users.factories import UserFactory


fake = faker.Faker()

# https://docs.getmoto.org/en/latest/docs/services/s3.html
# Note that this only works if the environment variable is set before the mock is initialized.
os.environ["MOTO_S3_CUSTOM_ENDPOINTS"] = settings.AWS_S3_ENDPOINT_URL


@pytest.fixture(name="superuser")
def superuser_fixture():
    return UserFactory(is_superuser=True, is_staff=True)


@pytest.fixture(name="image_content")
def image_content_fixture():
    img = Image.new("RGB", (1, 1), color="white")
    buffer = BytesIO()
    img.save(buffer, format="JPEG")
    return buffer.getvalue()


@mock_aws
def test_file_is_saved_with_logged_user(client, db, superuser, image_content):
    conn = boto3.client("s3", endpoint_url=settings.AWS_S3_ENDPOINT_URL, region_name="us-east-1")
    conn.create_bucket(Bucket=settings.AWS_STORAGE_BUCKET_NAME_PUBLIC)
    client.force_login(superuser)
    not_the_logged_in_user = UserFactory()

    response = client.post(
        reverse("admin:forum_file_publicfile_add"),
        {
            "file": SimpleUploadedFile("test.jpg", image_content, content_type="image/jpeg"),
            "user": not_the_logged_in_user.id,
            "keywords": fake.words(3),
        },
    )
    assert response.status_code == 302
    file = PublicFile.objects.get()
    assert file.user == superuser
