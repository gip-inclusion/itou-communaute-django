from django.conf import settings
from django.contrib.contenttypes.fields import GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.db.models import Count, Exists, OuterRef, Q
from django.urls import reverse
from machina.apps.forum_conversation.abstract_models import AbstractPost, AbstractTopic
from machina.models.abstract_models import DatedModel
from taggit.managers import TaggableManager

from lacommunaute.forum_member.shortcuts import get_forum_member_display_name
from lacommunaute.forum_upvote.models import UpVote
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

    def with_first_reply(self, previous_notification_at=None):
        """
        The first reply is the second approved post of a topic
        """
        first_reply_posts_count = 2

        qs = self.filter(posts_count=first_reply_posts_count)
        if previous_notification_at:
            qs = qs.filter(updated__gte=previous_notification_at)
        return qs


class Topic(AbstractTopic):
    likers = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name="topic_likes",
        blank=True,
        verbose_name=("Likers"),
    )

    tags = TaggableManager()

    def get_absolute_url(self, with_fqdn=False):
        absolute_url = reverse(
            "forum_conversation:topic",
            kwargs={
                "forum_pk": self.forum.pk,
                "forum_slug": self.forum.slug,
                "pk": self.pk,
                "slug": self.slug,
            },
        )

        # for tasks context, when we don't have access to request
        if with_fqdn:
            return f"{settings.COMMU_PROTOCOL}://{settings.COMMU_FQDN}{absolute_url}"

        return absolute_url

    def mails_to_notify(self):
        # we want to notify stakeholders of the topic, except the last poster.
        # stakeholders are:
        # - authenticated users who liked the topic
        # - authenticated users who upvoted one of the posts of the topic
        # - authenticated users who posted in the topic
        # - anonymous users who posted in the topic
        #
        # Notes :
        # `post.username` is the email of the anonymous poster
        # `post.username` is null for authenticated users, we use `post.poster.email` instead

        authenticated_qs = (
            User.objects.filter(
                Q(topic_likes=self)
                | Q(
                    upvotes__content_type=ContentType.objects.get_for_model(Post),
                    upvotes__object_id__in=self.posts.values("id"),
                )
                | Q(posts__topic=self)
            )
            .distinct()
            .values_list("email", flat=True)
        )
        anonymous_qs = (
            Post.objects.filter(topic=self).exclude(username__isnull=True).values_list("username", flat=True)
        )
        stakeholders_qs = sorted((authenticated_qs.union(anonymous_qs)))

        last_poster_email = self.last_post.username or self.last_post.poster.email

        return [email for email in stakeholders_qs if email != last_poster_email]

    @property
    def poster_email(self):
        return self.first_post.username or self.first_post.poster.email

    @property
    def is_certified(self):
        return hasattr(self, "certified_post")

    objects = TopicQuerySet().as_manager()


class Post(AbstractPost):
    username = models.EmailField(blank=True, null=True, verbose_name=("Adresse email"))

    upvotes = GenericRelation(UpVote, related_query_name="post")

    @property
    def poster_display_name(self):
        if self.username:
            return self.username.split("@")[0]
        return get_forum_member_display_name(self.poster)

    @property
    def is_certified(self):
        return hasattr(self, "certified_post")


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
