from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models


class UpVote(models.Model):
    voter = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="upvotes",
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        verbose_name="Voter",
    )

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveBigIntegerField()

    content_object = GenericForeignKey("content_type", "object_id")

    created_at = models.DateTimeField(auto_now_add=True, db_index=True, verbose_name="Creation date")
    objects = models.Manager()

    class Meta:
        unique_together = ["voter", "content_type", "object_id"]
        ordering = [
            "-created_at",
        ]
