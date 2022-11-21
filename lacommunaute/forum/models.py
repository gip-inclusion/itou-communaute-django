import datetime
import uuid

from dateutil.relativedelta import relativedelta
from django.contrib.auth.models import Group
from django.db import models
from django.db.models import Count, IntegerField, Subquery
from django.db.models.functions import Coalesce
from django.utils import timezone
from machina.apps.forum.abstract_models import AbstractForum
from machina.core.db.models import get_model


Topic = get_model("forum_conversation", "Topic")
Post = get_model("forum_conversation", "Post")
User = get_model("users", "User")


class Forum(AbstractForum):
    members_group = models.ForeignKey(Group, null=True, on_delete=models.CASCADE, verbose_name=("Members Group"))
    invitation_token = models.UUIDField(default=uuid.uuid4, unique=True)
    is_highlighted = models.BooleanField(default=False, verbose_name="affichée sur la homepage")
    is_private = models.BooleanField(default=False, verbose_name="privée")

    def get_stats(self, days_back):

        stats = {"days": [], "topics": [], "posts": [], "members": []}

        # to get a datetime timezone aware like "2022-11-16 00:00:00+01:00"
        now_date = timezone.now().date()
        today = datetime.datetime(year=now_date.year, month=now_date.month, day=now_date.day)
        today = timezone.make_aware(today)

        # create pks lists to filter by forum and its children
        pks = [self.pk]
        groups_pks = [self.members_group]
        for child in self.children.all():
            pks.append(child.id)
            groups_pks.append(child.members_group)

        qs = Forum.objects.filter(pk=self.pk)
        for i in range(days_back):
            day = today - relativedelta(days=i - 1)

            subquery_topics = Subquery(
                Topic.objects.filter(forum__in=pks, approved=True, created__lte=day)
                .exclude(approved=False)
                .values("approved")  # group by unique value to group forum and its children
                .annotate(count=Count("pk"))
                .values("count"),
                output_field=IntegerField(),
            )
            subquery_posts = Subquery(
                Post.objects.filter(
                    topic__forum__in=pks,
                    approved=True,
                    created__lte=day,
                )
                .exclude(topic__approved=False)
                .values("topic__approved")  # group by unique value to group forum and its children
                .annotate(count=Count("pk"))
                .values("count")
            )
            subquery_members = Subquery(
                User.objects.filter(date_joined__lte=day, groups__in=groups_pks, is_active=True, is_staff=False)
                .values("is_active")  # group by unique value to group forum and its children
                .annotate(count=Count("pk"))
                .values("count")
            )

            qs = qs.annotate(**{f"topics_count_day_{i}": Coalesce(subquery_topics, 0)})
            qs = qs.annotate(**{f"posts_count_day_{i}": Coalesce(subquery_posts, 0)})
            qs = qs.annotate(**{f"members_count_day_{i}": Coalesce(subquery_members, 0)})

            stats["days"].append(str(day.date()))

        # group stats by type for easily use in javascript
        forum_row = qs.first()
        for i in range(days_back):
            stats["topics"].append(getattr(forum_row, f"topics_count_day_{i}"))
            stats["posts"].append(getattr(forum_row, f"posts_count_day_{i}"))
            stats["members"].append(getattr(forum_row, f"members_count_day_{i}"))

        # reverse the lists to get correct order
        for stats_list in stats.items():
            stats_list[1].reverse()

        return stats
