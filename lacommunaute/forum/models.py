import uuid

from django.contrib.auth.models import Group
from django.db import models
from django.utils.functional import cached_property
from machina.apps.forum.abstract_models import AbstractForum

from lacommunaute.forum_conversation.models import Topic


class ForumQuerySet(models.QuerySet):
    def public(self):
        return self.filter(is_private=False)


class Forum(AbstractForum):
    members_group = models.ForeignKey(
        Group, blank=True, null=True, on_delete=models.CASCADE, verbose_name=("Members Group")
    )
    invitation_token = models.UUIDField(default=uuid.uuid4, unique=True)
    is_private = models.BooleanField(default=False, verbose_name="privée")
    is_newsfeed = models.BooleanField(default=False, verbose_name="fil d'actualité")

    objects = ForumQuerySet().as_manager()

    def get_unanswered_topics(self):
        return Topic.objects.unanswered().filter(forum__in=self.get_descendants(include_self=True))

    @cached_property
    def count_unanswered_topics(self):
        return self.get_unanswered_topics().count()
