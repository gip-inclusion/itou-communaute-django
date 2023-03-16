from django.conf import settings
from django.db import models
from machina.models.abstract_models import DatedModel

from lacommunaute.forum_conversation.models import Post, Topic


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


class CertifiedPost(DatedModel):
    topic = models.OneToOneField(
        Topic,
        related_name="certified_post",
        on_delete=models.CASCADE,
        verbose_name="Topic",
    )

    post = models.OneToOneField(
        Post,
        related_name="certified_post",
        on_delete=models.CASCADE,
        verbose_name="Post",
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="certified_posts",
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        verbose_name="User",
    )

    class Meta:
        ordering = [
            "-created",
        ]

    def __str__(self):
        return f"{self.post} - {self.topic} - {self.user}"

    def save(self, *args, **kwargs):
        if self.topic != self.post.topic:
            raise ValueError("The post is not link to the topic")
        super().save(*args, **kwargs)
