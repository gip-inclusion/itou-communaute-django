from django.conf import settings
from django.db import models
from django.urls import reverse
from machina.apps.forum_conversation.abstract_models import AbstractPost, AbstractTopic

from lacommunaute.forum_member.shortcuts import get_forum_member_display_name


class Topic(AbstractTopic):
    likers = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name="topic_likes",
        blank=True,
        verbose_name=("Likers"),
    )

    def get_absolute_url(self):
        return reverse(
            "forum_conversation:topic",
            kwargs={
                "forum_pk": self.forum.pk,
                "forum_slug": self.forum.slug,
                "pk": self.pk,
                "slug": self.slug,
            },
        )

    @property
    def poster_email(self):
        return self.first_post.username or self.first_post.poster.email


class Post(AbstractPost):
    username = models.EmailField(blank=True, null=True, verbose_name=("Adresse email"))

    @property
    def poster_display_name(self):

        if self.username:
            return self.username.split("@")[0]
        return get_forum_member_display_name(self.poster)
