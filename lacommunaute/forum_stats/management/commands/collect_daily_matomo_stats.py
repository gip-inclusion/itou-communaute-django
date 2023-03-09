from datetime import date

from dateutil.relativedelta import relativedelta
from django.core.management.base import BaseCommand

from lacommunaute.forum_stats.models import Stat
from lacommunaute.utils.matomo import collect_stats_from_matomo_api


class Command(BaseCommand):
    help = "Collecter les stats journalieres matomo, jusqu'à la veille de l'execution"

    def handle(self, *args, **options):

        from_date = Stat.objects.filter(period="day").order_by("-date").first().date + relativedelta(days=1)
        to_date = date.today() - relativedelta(days=1)

        collect_stats_from_matomo_api(from_date=from_date, to_date=to_date)

        self.stdout.write(self.style.SUCCESS("That's all, folks!"))
