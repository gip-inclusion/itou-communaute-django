from django.conf import settings
from django.db import models

from lacommunaute.forum_conversation.models import Post


class UpVote(models.Model):
    voter = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="upvotes",
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        verbose_name="Voter",
    )

    post = models.ForeignKey(
        Post,
        related_name="upvotes",
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        verbose_name="Post",
    )

    created_at = models.DateTimeField(auto_now_add=True, db_index=True, verbose_name="Creation date")
    objects = models.Manager()

    class Meta:
        unique_together = ["voter", "post"]
        ordering = [
            "-created_at",
        ]
