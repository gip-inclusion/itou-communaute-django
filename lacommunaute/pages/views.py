import logging
from typing import Any

from django.contrib.auth.mixins import UserPassesTestMixin
from django.db.models import CharField
from django.db.models.functions import Cast
from django.shortcuts import render
from django.utils import timezone
from django.utils.dateformat import format
from django.views.generic.base import TemplateView

from lacommunaute.event.models import Event
from lacommunaute.forum.enums import Kind as ForumKind
from lacommunaute.forum.models import Forum
from lacommunaute.forum_conversation.models import Topic
from lacommunaute.forum_stats.models import Stat
from lacommunaute.utils.json import extract_values_in_list
from lacommunaute.utils.math import percent


logger = logging.getLogger(__name__)


class StatistiquesPageView(TemplateView):
    template_name = "pages/statistiques.html"

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


class LandingPagesListView(UserPassesTestMixin, TemplateView):
    template_name = "pages/landing_pages.html"

    def test_func(self):
        return self.request.user.is_superuser


class HomeView(TemplateView):
    template_name = "pages/home.html"

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context["topics_public"] = Topic.objects.filter(forum__kind=ForumKind.PUBLIC_FORUM, approved=True).order_by(
            "-created"
        )[:4]
        context["forums_category"] = Forum.objects.filter(kind=ForumKind.PUBLIC_FORUM, parent__type=1).order_by(
            "-updated"
        )[:4]
        context["forum"] = Forum.objects.filter(kind=ForumKind.PUBLIC_FORUM, lft=1, level=0).first()
        context["upcoming_events"] = Event.objects.filter(date__gte=timezone.now()).order_by("date")[:4]
        return context


def accessibilite(request):
    return render(request, "pages/accessibilite.html")


def mentions_legales(request):
    return render(request, "pages/mentions_legales.html")


def politique_de_confidentialite(request):
    return render(request, "pages/politique_de_confidentialite.html")
