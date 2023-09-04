from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from machina.models.abstract_models import DatedModel
from storages.backends.s3boto3 import S3Boto3Storage

from lacommunaute.users.models import User


public_bucket = settings.AWS_STORAGE_BUCKET_NAME_PUBLIC


def validate_image_size(value):
    max_size = 1024 * 1024 * 8

    if value.size > max_size:
        raise ValidationError("L'image ne doit pas dépasser 1 Mo")


class PublicFile(DatedModel):
    # vincentporte : assumed this feature for superuser purpose will be break in dev environment
    # if Storages is not a S3 bucket
    file = models.ImageField(
        storage=S3Boto3Storage(bucket_name=public_bucket, file_overwrite=False, default_acl="public-read"),
        validators=[validate_image_size],
    )
    user = models.ForeignKey(User, on_delete=models.PROTECT)
    keywords = models.CharField(max_length=255)

    class Meta:
        verbose_name = "fichier public"
        verbose_name_plural = "fichiers publics"

    def get_file_url(self):
        return self.file.url.split("?")[0]
