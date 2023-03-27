import logging

from dateutil.relativedelta import relativedelta
from django.contrib.auth.mixins import UserPassesTestMixin
from django.db.models import CharField
from django.db.models.functions import Cast
from django.shortcuts import render
from django.utils import timezone
from django.views.generic.base import TemplateView

from lacommunaute.forum_stats.models import Stat
from lacommunaute.utils.json import extract_values_in_list


logger = logging.getLogger(__name__)


def contact(request):
    return render(request, "pages/contact.html")


class StatistiquesPageView(TemplateView):
    template_name = "pages/statistiques.html"

    def get_context_data(self, **kwargs):
        indicator_names = [
            "nb_uniq_engaged_visitors",
            "nb_uniq_visitors",
            "nb_uniq_active_visitors",
        ]
        after_date = timezone.now() - relativedelta(months=3)
        datas = (
            Stat.objects.filter(period="day", name__in=indicator_names, date__gte=after_date)
            .values("name", "value")
            .annotate(date=Cast("date", CharField()))
        )

        context = super().get_context_data(**kwargs)
        context["stats"] = extract_values_in_list(datas, indicator_names)

        return context


class LandingPagesListView(UserPassesTestMixin, TemplateView):
    template_name = "pages/landing_pages.html"

    def test_func(self):
        return self.request.user.is_superuser


def accessibilite(request):
    return render(request, "pages/accessibilite.html")


def trigger_error(request):
    if request.POST:
        raise Exception("%s error: %s" % (request.POST.get("status_code"), request.POST.get("error_message")))

    print(1 / 0)  # Should raise a ZeroDivisionError.
