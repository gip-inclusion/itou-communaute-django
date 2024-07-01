import datetime
import logging

from dateutil.relativedelta import relativedelta
from django.db.models import Avg, CharField, Count, Q
from django.db.models.functions import Cast
from django.utils.dateformat import format
from django.utils.timezone import localdate
from django.views.generic.base import TemplateView
from django.views.generic.dates import WeekArchiveView

from lacommunaute.forum.models import Forum
from lacommunaute.stats.models import ForumStat, Stat
from lacommunaute.surveys.models import DSP
from lacommunaute.utils.json import extract_values_in_list
from lacommunaute.utils.math import percent


logger = logging.getLogger(__name__)


def get_daily_visits_stats(from_date, to_date):
    indicator_names = [
        "nb_uniq_visitors",
        "nb_uniq_engaged_visitors",
    ]
    datas = (
        Stat.objects.filter(period="day", name__in=indicator_names, date__gte=from_date, date__lte=to_date)
        .values("name", "value")
        .annotate(date=Cast("date", CharField()))
    )
    return extract_values_in_list(datas, indicator_names)


class StatistiquesPageView(TemplateView):
    template_name = "stats/statistiques.html"

    def get_funnel_data(self):
        qs = Stat.objects.current_month_datas()

        stats = {
            "period": None,
            "nb_uniq_visitors": 0,
            "nb_uniq_active_visitors": 0,
            "nb_uniq_engaged_visitors": 0,
        }

        if qs.filter(name="nb_uniq_visitors").exists():
            stats["period"] = format(qs.get(name="nb_uniq_visitors")["date"], "F Y")
            stats["nb_uniq_visitors"] = qs.get(name="nb_uniq_visitors")["value"]

        if qs.filter(name="nb_uniq_active_visitors").exists():
            stats["nb_uniq_active_visitors"] = qs.get(name="nb_uniq_active_visitors")["value"]

        if qs.filter(name="nb_uniq_engaged_visitors").exists():
            stats["nb_uniq_engaged_visitors"] = qs.get(name="nb_uniq_engaged_visitors")["value"]

        stats["activation_percent"] = percent(stats["nb_uniq_active_visitors"], stats["nb_uniq_visitors"])
        stats["engagement_percent"] = percent(stats["nb_uniq_engaged_visitors"], stats["nb_uniq_active_visitors"])
        return stats

    def get_monthly_visitors(self):
        indicator_names = ["nb_uniq_visitors_returning"]
        datas = (
            Stat.objects.filter(period="month", name__in=indicator_names)
            .values("name", "value")
            .annotate(date=Cast("date", CharField()))
        )
        return extract_values_in_list(datas, indicator_names)

    def get_dsp_count(self):
        return DSP.objects.count()

    def get_context_data(self, **kwargs):
        yesterday = localdate() - relativedelta(days=1)
        context = super().get_context_data(**kwargs)
        context["stats"] = get_daily_visits_stats(from_date=yesterday - relativedelta(days=89), to_date=yesterday)
        context["impact"] = self.get_monthly_visitors()
        context["dsp_count"] = self.get_dsp_count()
        context = {**context, **self.get_funnel_data()}

        return context


class BaseDetailStatsView(TemplateView):
    def get_detailled_stats(self):
        datas = (
            Stat.objects.filter(
                period=self.period,
                name__in=self.indicator_names,
                date__gt=localdate() - relativedelta(months=self.months),
            )
            .values("name", "value")
            .annotate(date=Cast("date", CharField()))
        )
        return extract_values_in_list(datas, self.indicator_names)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["stats"] = self.get_detailled_stats()
        context["box_title"] = self.box_title
        return context


class MonthlyVisitorsView(BaseDetailStatsView):
    template_name = "stats/monthly_visitors.html"
    box_title = "Utilisateurs uniques mensuels"
    indicator_names = [
        "nb_uniq_visitors",
        "nb_uniq_active_visitors",
        "nb_uniq_engaged_visitors",
        "nb_uniq_visitors_returning",
    ]
    period = "month"
    months = 9


class DailyDSPView(BaseDetailStatsView):
    template_name = "stats/daily_dsp.html"
    box_title = "Diagnostics Parcours IAE quotidiens"
    indicator_names = ["dsp"]
    period = "day"
    months = 3


class ForumStatWeekArchiveView(WeekArchiveView):
    template_name = "stats/forum_stat_week_archive.html"
    date_field = "date"
    queryset = ForumStat.objects.filter(period="week").select_related("forum")
    week_format = "%W"
    make_object_list = True
    context_object_name = "forum_stats"
    ordering = ["date", "-visits"]
    paginate_by = 15

    def get_dates_of_the_week(self):
        start_date = datetime.date(self.get_year(), 1, 1) + datetime.timedelta(weeks=self.get_week() - 1)
        return start_date, start_date + datetime.timedelta(days=6)

    def get_most_rated_forums(self, start_date, end_date):
        return (
            Forum.objects.annotate(avg_rating=Avg("forumrating__rating"))
            .filter(avg_rating__isnull=False)
            .annotate(
                rating_count=Count(
                    "forumrating",
                    filter=Q(
                        forumrating__created__gte=start_date, forumrating__created__lt=end_date + relativedelta(days=1)
                    ),
                )
            )
            .filter(rating_count__gt=1)
            .order_by("-rating_count", "avg_rating", "id")
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        start_date, end_date = self.get_dates_of_the_week()
        context["end_date"] = end_date
        context["stats"] = get_daily_visits_stats(from_date=end_date - relativedelta(days=89), to_date=end_date)
        context["rated_forums"] = self.get_most_rated_forums(start_date, end_date)
        return context
