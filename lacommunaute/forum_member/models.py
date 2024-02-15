from dateutil.relativedelta import relativedelta
from django.db import models
from django.utils import timezone
from machina.apps.forum_member.abstract_models import AbstractForumProfile

from lacommunaute.forum_member.shortcuts import get_forum_member_display_name


class ForumProfileQuerySet(models.QuerySet):
    def power_users(self):
        return (
            self.filter(user__posts__created__gte=timezone.now() - relativedelta(days=30))
            .annotate(user_posts_count=models.Count("user__posts"))
            .filter(user_posts_count__gte=3)
            .order_by("-user_posts_count")
            .select_related("user")
            .prefetch_related("user__posts")
        )


class ForumProfile(AbstractForumProfile):
    objects = ForumProfileQuerySet().as_manager()

    def __str__(self):
        return get_forum_member_display_name(self.user)
