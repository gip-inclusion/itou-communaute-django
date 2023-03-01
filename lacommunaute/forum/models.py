import uuid

from dateutil.relativedelta import relativedelta
from django.contrib.auth.models import Group
from django.db import models
from django.db.models.functions import TruncWeek
from django.utils import timezone
from django.utils.functional import cached_property
from machina.apps.forum.abstract_models import AbstractForum

from config.settings.base import DAYS_IN_A_PERIOD
from lacommunaute.forum_conversation.forum_polls.models import TopicPollVote
from lacommunaute.forum_conversation.models import Post, Topic
from lacommunaute.forum_upvote.models import UpVote
from lacommunaute.utils.enums import PeriodAggregation
from lacommunaute.utils.stats import count_objects_per_period, format_counts_of_objects_for_timeline_chart


class Forum(AbstractForum):
    members_group = models.ForeignKey(Group, null=True, on_delete=models.CASCADE, verbose_name=("Members Group"))
    invitation_token = models.UUIDField(default=uuid.uuid4, unique=True)
    is_private = models.BooleanField(default=False, verbose_name="privée")
    target_audience = models.IntegerField(default=0)

    def get_stats(self, period_back):

        start_date = timezone.localdate() - relativedelta(days=period_back * DAYS_IN_A_PERIOD - 1)
        forums = self.get_family()

        datas = (
            count_objects_per_period(
                Topic.objects.filter(forum__in=forums, created__gte=start_date).annotate(period=TruncWeek("created")),
                "topics",
            )
            + count_objects_per_period(
                Post.objects.filter(topic__forum__in=forums, created__gte=start_date).annotate(
                    period=TruncWeek("created")
                ),
                "posts",
            )
            + count_objects_per_period(
                UpVote.objects.filter(post__topic__forum__in=forums, created_at__gte=start_date).annotate(
                    period=TruncWeek("created_at")
                ),
                "upvotes",
            )
            + count_objects_per_period(
                TopicPollVote.objects.filter(
                    poll_option__poll__topic__forum__in=forums, timestamp__gte=start_date
                ).annotate(period=TruncWeek("timestamp")),
                "pollvotes",
            )
        )
        return format_counts_of_objects_for_timeline_chart(datas, period=PeriodAggregation.WEEK)

    @cached_property
    def count_unanswered_topics(self):
        return (
            Topic.objects.exclude(type=Topic.TOPIC_ANNOUNCE)
            .exclude(approved=False)
            .exclude(status=Topic.TOPIC_LOCKED)
            .filter(posts_count=1, forum__in=self.get_descendants(include_self=True))
            .count()
        )
