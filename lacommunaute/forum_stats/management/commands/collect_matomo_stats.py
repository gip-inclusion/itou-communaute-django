from datetime import date

from dateutil.relativedelta import relativedelta
from django.core.management.base import BaseCommand

from lacommunaute.forum_stats.models import Stat
from lacommunaute.utils.matomo import collect_stats_from_matomo_api


class Command(BaseCommand):
    help = "Collecter les stats matomo, jusqu'à la veille de l'execution"

    def add_arguments(self, parser):
        parser.add_argument("--period", type=str, help="['day','week','month']", default="day")

    def handle(self, *args, **options):

        period = options["period"]

        from_date = Stat.objects.filter(period=period).order_by("-date").first()

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

        self.stdout.write(self.style.SUCCESS("That's all, folks!"))
