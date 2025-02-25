from datetime import date
from logging import getLogger

from dateutil.relativedelta import relativedelta
from django.core.management.base import BaseCommand

from lacommunaute.stats.models import Stat
from lacommunaute.utils.matomo import collect_stats_from_matomo_api


logger = getLogger("commands")

matomo_stats_names = [
    "nb_uniq_visitors",
    "nb_uniq_visitors_returning",
    "nb_uniq_active_visitors",
    "nb_uniq_engaged_visitors",
]


def get_initial_from_date(period):
    return Stat.objects.filter(period=period, name__in=matomo_stats_names).order_by("-date").first()


class Command(BaseCommand):
    help = "Collecter les stats matomo, jusqu'à la veille de l'execution"

    def add_arguments(self, parser):
        parser.add_argument("--period", type=str, help="['day','week','month']", default="day")

    def handle(self, *args, **options):
        period = options["period"]

        from_date = get_initial_from_date(period)

        if from_date:
            if period == "day":
                from_date = from_date.date + relativedelta(days=1)
            elif period == "week":
                from_date = from_date.date + relativedelta(days=7)
            else:
                from_date = from_date.date + relativedelta(months=1)
        else:
            from_date = date(2022, 12, 1)

        to_date = date.today() - relativedelta(days=1)

        collect_stats_from_matomo_api(from_date=from_date, to_date=to_date, period=period)

        logger.info("That's all, folks!")
