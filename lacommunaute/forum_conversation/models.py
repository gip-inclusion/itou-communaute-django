from django.conf import settings
from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from machina.apps.forum_conversation.abstract_models import AbstractPost, AbstractTopic


class Topic(AbstractTopic):
    likers = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name="topic_likes",
        blank=True,
        verbose_name=("Likers"),
    )

    TOPIC_POST, TOPIC_STICKY, TOPIC_ANNOUNCE, TOPIC_JOBOFFER = 0, 1, 2, 3
    TYPE_CHOICES = (
        (TOPIC_POST, _("Default topic")),
        (TOPIC_STICKY, _("Sticky")),
        (TOPIC_ANNOUNCE, _("Announce")),
        (TOPIC_JOBOFFER, _("Job offer")),
    )
    type = models.PositiveSmallIntegerField(
        choices=TYPE_CHOICES,
        db_index=True,
        verbose_name=_("Topic type"),
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


class Post(AbstractPost):
    username = models.EmailField(blank=True, null=True, verbose_name=("Adresse email"))
