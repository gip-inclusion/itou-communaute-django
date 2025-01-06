import logging

from dateutil.relativedelta import relativedelta
from django.db.models import Avg, CharField, Count, OuterRef, Subquery, Sum
from django.db.models.functions import Cast
from django.shortcuts import render
from django.utils.dateformat import format
from django.utils.timezone import localdate
from django.views import View
from django.views.generic.base import TemplateView

from lacommunaute.forum.models import Forum, ForumRating
from lacommunaute.stats.models import Stat
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


class DocumentStatsView(View):
    def get_objects_with_stats_and_ratings(self):
        objects = (
            Forum.objects.filter(parent__type=Forum.FORUM_CAT, forumstat__period="week")
            .annotate(sum_visits=Sum("forumstat__visits"))
            .annotate(sum_time_spent=Sum("forumstat__time_spent"))
            .select_related("parent", "partner")
            .order_by("id")
        )
        ratings = ForumRating.objects.filter(forum=OuterRef("pk")).values("forum")
        return objects.annotate(
            avg_rating=Subquery(ratings.annotate(avg_rating=Avg("rating")).values("avg_rating")),
            count_rating=Subquery(ratings.annotate(count_rating=Count("rating")).values("count_rating")),
        )

    def get_sort_fields(self):
        return [
            {"key": "parent", "label": "Catégorie"},
            {"key": "sum_time_spent", "label": "Temps de lecture"},
            {"key": "sum_visits", "label": "Nombre de Visites"},
            {"key": "count_rating", "label": "Nombres de notations"},
            {"key": "avg_rating", "label": "Moyenne des notations"},
        ]

    def get(self, request, *args, **kwargs):
        objects = self.get_objects_with_stats_and_ratings()
        sort_key = (
            request.GET.get("sort")
            if request.GET.get("sort") in [field["key"] for field in self.get_sort_fields()]
            else "sum_time_spent"
        )
        objects = objects.order_by("-" + sort_key)

        return render(
            request,
            "stats/documents.html",
            {
                "objects": objects,
                "sort_key": sort_key,
                "sort_fields": self.get_sort_fields(),
            },
        )
