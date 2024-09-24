from django.conf import settings
from django.db import models
from django.utils.encoding import force_str
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _

# TODO: define it in the project instead of importing it from machina
from machina.models.fields import MarkupTextField
from storages.backends.s3boto3 import S3Boto3Storage

from lacommunaute.utils.html import wrap_iframe_in_div_tag
from lacommunaute.utils.validators import validate_image_size


class DatedModel(models.Model):
    created = models.DateTimeField(auto_now_add=True, verbose_name=_("Creation date"))
    updated = models.DateTimeField(auto_now=True, verbose_name=_("Update date"))

    class Meta:
        abstract = True


class Publication(DatedModel):
    name = models.CharField(max_length=100, verbose_name=_("Name"), unique=True)
    slug = models.SlugField(max_length=255, verbose_name=_("Slug"))

    description = MarkupTextField(verbose_name=_("Description"), null=True, blank=True)
    short_description = models.CharField(max_length=400, verbose_name=_("Short Description"))
    image = models.ImageField(
        storage=S3Boto3Storage(bucket_name=settings.AWS_STORAGE_BUCKET_NAME, file_overwrite=False),
        validators=[validate_image_size],
        blank=True,
        null=True,
    )

    class Meta:
        abstract = True

    def __str__(self):
        return f"{self.name}"

    def save(self, *args, **kwargs):
        self.slug = slugify(force_str(self.name), allow_unicode=True)
        if self.description:
            self.description.raw = wrap_iframe_in_div_tag(self.description.raw)
        super().save(*args, **kwargs)
