from django.conf import settings
from django.db import models
from django.urls import reverse
from django.utils.encoding import force_str
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _
from machina.models.abstract_models import DatedModel
from machina.models.fields import MarkupTextField
from storages.backends.s3boto3 import S3Boto3Storage

from lacommunaute.utils.validators import validate_image_size


class Partner(DatedModel):
    name = models.CharField(max_length=100, verbose_name="Nom", unique=True)
    slug = models.SlugField(max_length=255, verbose_name="Slug")
    short_description = models.CharField(
        max_length=400, blank=True, null=True, verbose_name="Description courte (SEO)"
    )
    description = MarkupTextField(verbose_name="Description", null=True, blank=True)
    logo = models.ImageField(
        storage=S3Boto3Storage(bucket_name=settings.AWS_STORAGE_BUCKET_NAME, file_overwrite=False),
        validators=[validate_image_size],
        upload_to="logos/",
        help_text="1200x600 recommandé",
    )
    url = models.URLField(verbose_name="Lien vers le site du partenaire", null=True, blank=True)

    objects = models.Manager()

    class Meta:
        verbose_name = _("Partner")
        verbose_name_plural = _("Partners")
        ordering = ["-updated"]

    def __str__(self):
        return f"{self.name}"

    def save(self, *args, **kwargs):
        self.slug = slugify(force_str(self.name), allow_unicode=True)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("partner:detail", kwargs={"slug": self.slug, "pk": self.pk})
