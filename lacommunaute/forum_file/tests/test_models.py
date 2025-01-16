import faker
import moto
import pytest
from django.conf import settings
from django.db.models.fields.files import ImageField

from lacommunaute.forum_file.models import PublicFile
from lacommunaute.users.factories import UserFactory


fake = faker.Faker()


@pytest.fixture(name="s3_bucket")
def s3_bucket_fixture():
    with moto.mock_aws():
        yield settings.AWS_STORAGE_BUCKET_NAME_PUBLIC


@pytest.fixture(name="public_file")
def public_file_fixture(s3_bucket):
    public_file = PublicFile.objects.create(
        file="test.jpg",
        user=UserFactory(),
        keywords=fake.words(3),
    )
    return public_file


def test_get_file_url(db, public_file):
    expected_file_url = f"{settings.MEDIA_URL}{settings.AWS_STORAGE_BUCKET_NAME_PUBLIC}/{public_file.file.name}"
    assert public_file.get_file_url() == expected_file_url


def test_file_field_is_imagefield(db):
    assert isinstance(PublicFile._meta.get_field("file"), ImageField)
