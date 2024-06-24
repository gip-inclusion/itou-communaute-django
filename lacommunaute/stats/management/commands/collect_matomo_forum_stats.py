from datetime import date

from dateutil.relativedelta import relativedelta
from django.core.management.base import BaseCommand

from lacommunaute.stats.models import ForumStat
from lacommunaute.utils.date import get_last_sunday
from lacommunaute.utils.matomo import collect_forum_stats_from_matomo_api


class Command(BaseCommand):
    help = "Collecter les stats des forum dans matomo, jusqu'au dimanche précédent l'execution"

    def handle(self, *args, **options):
        period = "week"

        from_date = ForumStat.objects.filter(period=period).order_by("-date").first()

        if from_date:
            from_date = from_date.date + relativedelta(days=7)
        else:
            from_date = date(2023, 10, 2)

        to_date = get_last_sunday(date.today())

        collect_forum_stats_from_matomo_api(from_date=from_date, to_date=to_date, period=period)

        self.stdout.write(self.style.SUCCESS("That's all, folks!"))
