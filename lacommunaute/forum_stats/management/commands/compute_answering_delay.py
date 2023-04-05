# vincenporte ~ untested code
# TODO: refactor it code base and test it

from datetime import timedelta
from typing import Dict

from django.core.management.base import BaseCommand
from django.db.models import F, OuterRef, Subquery
from django.db.models.query import QuerySet

from lacommunaute.forum.models import Forum
from lacommunaute.forum_conversation.models import Post, Topic


def get_answered_topics_of_a_month(month: int, year: int) -> QuerySet:
    related_posts = Post.objects.filter(topic=OuterRef("pk")).order_by("created")
    return Topic.objects.filter(
        created__year=year, created__month=month, posts_count__gte=2, forum__in=Forum.objects.public()
    ).annotate(
        question=Subquery(related_posts.values("created")[:1]),
        first_answer=Subquery(related_posts.values("created")[1:2]),
        time_diff_seconds=F("first_answer") - F("question"),
    )


def get_human_readable_delay(delay: timedelta) -> str:
    days = delay.days
    hours, remainder = divmod(delay.seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"{days} jours, {hours} heures, {minutes} minutes et {seconds} secondes"


def min_median_max_values(queryset: QuerySet, term: str) -> Dict[str, str]:
    count = queryset.count()
    ordered_list = queryset.values_list(term, flat=True).order_by(term)
    values = {"min": ordered_list[0], "median": ordered_list[int(round(count / 2))], "max": ordered_list[count - 1]}
    return {k: get_human_readable_delay(v) for k, v in values.items()}


class Command(BaseCommand):
    help = "Calculer les délais de réponse pour un mois donné"

    def add_arguments(self, parser):
        parser.add_argument("--year", type=int, help="year", default=2023)
        parser.add_argument("--month", type=int, help="month without leading zero", default=3)

    def handle(self, *args, **options):

        month = options["month"]
        year = options["year"]

        values = min_median_max_values(get_answered_topics_of_a_month(month, year), "time_diff_seconds")
        self.stdout.write(self.style.SUCCESS(f"{month}/{year}: {values}"))
        self.stdout.write(self.style.SUCCESS("That's all, folks!"))
