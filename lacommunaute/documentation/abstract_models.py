from django.conf import settings
from django.db import models
from django.utils.encoding import force_str
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _
from machina.models.fields import MarkupTextField
from storages.backends.s3boto3 import S3Boto3Storage

from lacommunaute.utils.validators import validate_image_size


class AbstractDatedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class AbstractPublication(AbstractDatedModel):
    name = models.CharField(max_length=100, verbose_name=_("Name"))
    slug = models.SlugField(max_length=255, verbose_name=_("Slug"), unique=True)

    description = MarkupTextField(verbose_name=_("Description"), null=True, blank=True)
    short_description = models.CharField(max_length=400, verbose_name="Description courte (SEO)")
    image = models.ImageField(
        blank=True,
        null=True,
        storage=S3Boto3Storage(bucket_name=settings.AWS_STORAGE_BUCKET_NAME, file_overwrite=False),
        validators=[validate_image_size],
    )

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        self.slug = slugify(force_str(self.name), allow_unicode=True)
        super().save(*args, **kwargs)
