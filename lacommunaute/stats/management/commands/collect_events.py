# vincenporte ~ assumed quick'n'dirty solution
# TODO: refactor it code base and test it

import json
from datetime import datetime

from dateutil.relativedelta import relativedelta
from django.core.management.base import BaseCommand
from django.db.models import Count
from django.db.models.functions import TruncMonth, TruncWeek
from django.utils import timezone

from lacommunaute.forum_conversation.models import Post
from lacommunaute.forum_upvote.models import CertifiedPost, UpVote
from lacommunaute.utils.matomo import get_matomo_data


def save_to_json(stats, period):
    with open(f"exports/{period}ly_events.json", "w") as f:
        json.dump(stats, f)


def collect_matomo_events(period, search_date, stats):
    while search_date < timezone.now():
        datas = get_matomo_data(period=period, search_date=search_date, method="Events.getCategory")

        for data in datas:
            stats.append(
                {"period": search_date.strftime("%Y-%m-%d"), "label": data["label"], "value": data["nb_events"]}
            )
            for subdata in data["subtable"]:
                stats.append(
                    {
                        "period": search_date.strftime("%Y-%m-%d"),
                        "label": subdata["label"],
                        "value": subdata["nb_events"],
                    }
                )

        if period == "month":
            search_date += relativedelta(months=1)
        elif period == "week":
            search_date += relativedelta(days=7)

    return stats


def collect_db_events(period, search_date, stats):
    if period == "month":
        field_func = TruncMonth
    elif period == "week":
        field_func = TruncWeek

    posts = (
        Post.objects.filter(created__gte=search_date)
        .annotate(period=field_func("created"))
        .values("period")
        .annotate(count=Count("id"))
    )
    upvotes = (
        UpVote.objects.filter(created_at__gte=search_date)
        .annotate(period=field_func("created_at"))
        .values("period")
        .annotate(count=Count("id"))
    )
    certified_posts = (
        CertifiedPost.objects.filter(created__gte=search_date)
        .annotate(period=field_func("created"))
        .values("period")
        .annotate(count=Count("id"))
    )

    for post in posts:
        stats.append({"period": post["period"].strftime("%Y-%m-%d"), "label": "post", "value": post["count"]})
    for upvote in upvotes:
        stats.append({"period": upvote["period"].strftime("%Y-%m-%d"), "label": "upvote", "value": upvote["count"]})
    for certified_post in certified_posts:
        stats.append(
            {
                "period": certified_post["period"].strftime("%Y-%m-%d"),
                "label": "certified_post",
                "value": certified_post["count"],
            }
        )
    return stats


class Command(BaseCommand):
    help = "Collecter le nombre d'evenements par semaine et par mois"

    def handle(self, *args, **options):
        for period, search_date in (
            ("month", timezone.make_aware(datetime(2023, 1, 1), timezone.get_current_timezone())),
            ("week", timezone.make_aware(datetime(2023, 1, 2), timezone.get_current_timezone())),
        ):
            self.stdout.write(f"Collecting {period}ly events from {search_date}")
            stats = []
            stats = collect_matomo_events(period, search_date, stats)
            stats = collect_db_events(period, search_date, stats)
            save_to_json(stats, period)

        self.stdout.write(self.style.SUCCESS("That's all, folks!"))
