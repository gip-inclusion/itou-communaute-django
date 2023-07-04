from django.conf import settings
from django.db import models
from django.db.models import Count, Exists, OuterRef
from django.urls import reverse
from machina.apps.forum_conversation.abstract_models import AbstractPost, AbstractTopic
from taggit.managers import TaggableManager

from lacommunaute.forum_member.shortcuts import get_forum_member_display_name
from lacommunaute.users.models import User


class TopicQuerySet(models.QuerySet):
    def unanswered(self):
        return (
            self.exclude(approved=False)
            .exclude(status=Topic.TOPIC_LOCKED)
            .exclude(type=Topic.TOPIC_ANNOUNCE)
            .filter(posts_count=1)
        )

    def optimized_for_topics_list(self, user_id):
        return (
            self.exclude(approved=False)
            .filter(type__in=[Topic.TOPIC_POST, Topic.TOPIC_STICKY])
            .annotate(likes=Count("likers"))
            .annotate(has_liked=Exists(User.objects.filter(topic_likes=OuterRef("id"), id=user_id)))
            .select_related(
                "forum",
                "poster",
                "poster__forum_profile",
                "first_post",
                "first_post__poster",
                "certified_post",
                "certified_post__post",
                "certified_post__post__poster",
            )
            .prefetch_related(
                "poll",
                "poll__options",
                "poll__options__votes",
                "first_post__attachments",
                "certified_post__post__attachments",
                "tags",
            )
            .order_by("-last_post_on")
        )


class Topic(AbstractTopic):
    likers = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name="topic_likes",
        blank=True,
        verbose_name=("Likers"),
    )

    tags = TaggableManager()

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

    @property
    def is_certified(self):
        return hasattr(self, "certified_post")

    objects = TopicQuerySet().as_manager()


class Post(AbstractPost):
    username = models.EmailField(blank=True, null=True, verbose_name=("Adresse email"))

    @property
    def poster_display_name(self):
        if self.username:
            return self.username.split("@")[0]
        return get_forum_member_display_name(self.poster)

    @property
    def is_certified(self):
        return hasattr(self, "certified_post")
