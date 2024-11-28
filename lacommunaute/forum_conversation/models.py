from django.conf import settings
from django.contrib.contenttypes.fields import GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.db.models import Q
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from machina.apps.forum_conversation.abstract_models import AbstractPost, AbstractTopic
from machina.models.abstract_models import DatedModel
from taggit.managers import TaggableManager

from lacommunaute.forum_conversation.signals import post_create
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
            .select_related(
                "forum",
                "poster",
                "poster__forum_profile",
                "first_post",
                "first_post__poster",
            )
            .order_by("-last_post_on")
        )

    def optimized_for_topics_list(self, user_id):
        return (
            self.exclude(approved=False)
            .filter(type__in=[Topic.TOPIC_POST, Topic.TOPIC_STICKY, Topic.TOPIC_ANNOUNCE])
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

    def mails_to_notify_topic_head(self):
        forum_upvoters_qs = User.objects.filter(id__in=self.forum.upvotes.all().values("voter_id")).values_list(
            "email", flat=True
        )
        return [email for email in forum_upvoters_qs]

    def mails_to_notify_replies(self):
        # we want to notify stakeholders of the topic, except the last poster.
        # stakeholders are:
        # - authenticated users who upvoted one of the posts of the topic
        # - authenticated users who posted in the topic
        # - anonymous users who posted in the topic
        #
        # Notes :
        # `post.username` is the email of the anonymous poster
        # `post.username` is null for authenticated users, we use `post.poster.email` instead

        authenticated_qs = (
            User.objects.filter(
                Q(
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

    def mails_to_notify(self):
        if self.last_post.is_topic_head:
            return self.mails_to_notify_topic_head()
        return self.mails_to_notify_replies()

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

    @property
    def is_first_reply(self):
        """First reply is the second post in a topic"""
        return self.is_topic_tail and self.topic.posts_count == 2

    def save(self, *args, **kwargs):
        created = not self.pk
        super().save(*args, **kwargs)
        if created and (self.is_topic_tail and not self.is_topic_head):
            post_create.send(sender=self.__class__, instance=self)


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
        verbose_name = _("Certified Post")
        verbose_name_plural = _("Certified Posts")

    def __str__(self):
        return f"{self.post} - {self.topic} - {self.user}"

    def save(self, *args, **kwargs):
        if self.topic != self.post.topic:
            raise ValueError("The post is not link to the topic")
        super().save(*args, **kwargs)
