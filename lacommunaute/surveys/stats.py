from datetime import date, datetime, time

from dateutil.relativedelta import relativedelta
from django.db.models import Count, Value
from django.db.models.functions import TruncDate
from django.utils import timezone

from lacommunaute.forum_stats.models import Stat
from lacommunaute.surveys.models import DSP


def collect_dsp_stats():
    period = "day"

    from_date = (
        Stat.objects.filter(name="dsp", period=period).latest("date").date + relativedelta(days=1)
        if Stat.objects.filter(name="dsp", period=period).exists()
        else date(2024, 1, 1)
    )

    stats = (
        DSP.objects.filter(created__gte=timezone.make_aware(datetime.combine(from_date, time())))
        .annotate(date=TruncDate("created"))
        .values("date")
        .annotate(value=Count("id"), name=Value("dsp"), period=Value("day"))
        .order_by("date")
    )

    return from_date, len(Stat.objects.bulk_create([Stat(**stat) for stat in stats]))
