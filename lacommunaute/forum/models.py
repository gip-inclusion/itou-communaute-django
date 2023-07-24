import uuid

from django.contrib.auth.models import Group
from django.contrib.contenttypes.fields import GenericRelation
from django.db import models
from django.urls import reverse
from django.utils.functional import cached_property
from machina.apps.forum.abstract_models import AbstractForum

from lacommunaute.forum.enums import Kind as Forum_Kind
from lacommunaute.forum_conversation.models import Topic
from lacommunaute.forum_upvote.models import UpVote


class ForumQuerySet(models.QuerySet):
    def public(self):
        return self.filter(kind=Forum_Kind.PUBLIC_FORUM)


class Forum(AbstractForum):
    members_group = models.ForeignKey(
        Group, blank=True, null=True, on_delete=models.CASCADE, verbose_name=("Members Group")
    )
    invitation_token = models.UUIDField(default=uuid.uuid4, unique=True)
    kind = models.CharField(
        max_length=20, choices=Forum_Kind.choices, default=Forum_Kind.PUBLIC_FORUM, verbose_name="Type"
    )
    short_description = models.CharField(
        max_length=400, blank=True, null=True, verbose_name="Description courte (SEO)"
    )

    upvotes = GenericRelation(UpVote, related_query_name="forum")

    objects = ForumQuerySet().as_manager()

    def get_absolute_url(self):
        return reverse(
            "forum_extension:forum",
            kwargs={
                "pk": self.pk,
                "slug": self.slug,
            },
        )

    def get_unanswered_topics(self):
        return Topic.objects.unanswered().filter(forum__in=self.get_descendants(include_self=True))

    @cached_property
    def count_unanswered_topics(self):
        return self.get_unanswered_topics().count()

    def upvotes_count(self):
        return self.upvotes.count()
