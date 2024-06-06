import logging

from dateutil.relativedelta import relativedelta
from django.db.models import CharField
from django.db.models.functions import Cast
from django.utils import timezone
from django.utils.dateformat import format
from django.utils.timezone import localdate
from django.views.generic.base import TemplateView

from lacommunaute.forum_stats.models import Stat
from lacommunaute.utils.json import extract_values_in_list
from lacommunaute.utils.math import percent


logger = logging.getLogger(__name__)


class StatistiquesPageView(TemplateView):
    template_name = "forum_stats/statistiques.html"

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

    def get_daily_stats(self):
        indicator_names = [
            "nb_uniq_visitors",
            "nb_uniq_active_visitors",
            "nb_uniq_engaged_visitors",
        ]
        after_date = timezone.now() - timezone.timedelta(days=90)
        datas = (
            Stat.objects.filter(period="day", name__in=indicator_names, date__gte=after_date)
            .values("name", "value")
            .annotate(date=Cast("date", CharField()))
        )
        return extract_values_in_list(datas, indicator_names)

    def get_monthly_visitors(self):
        indicator_names = ["nb_uniq_visitors_returning"]
        datas = (
            Stat.objects.filter(period="month", name__in=indicator_names)
            .values("name", "value")
            .annotate(date=Cast("date", CharField()))
        )
        return extract_values_in_list(datas, indicator_names)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["stats"] = self.get_daily_stats()
        context["impact"] = self.get_monthly_visitors()
        context = {**context, **self.get_funnel_data()}

        return context


class MonthlyVisitorsViews(TemplateView):
    template_name = "forum_stats/monthly_visitors.html"

    def get_monthly_visitors(self):
        indicator_names = [
            "nb_uniq_visitors",
            "nb_uniq_active_visitors",
            "nb_uniq_engaged_visitors",
            "nb_uniq_visitors_returning",
        ]
        datas = (
            Stat.objects.filter(
                period="month", name__in=indicator_names, date__gt=localdate() - relativedelta(months=9)
            )
            .values("name", "value")
            .annotate(date=Cast("date", CharField()))
        )
        return extract_values_in_list(datas, indicator_names)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["monthly_visitors"] = self.get_monthly_visitors()
        return context
