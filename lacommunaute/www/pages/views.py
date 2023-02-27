import logging

from django.db.models import CharField
from django.db.models.functions import Cast
from django.shortcuts import render
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
            "nb_unique_contributors",
            "nb_uniq_visitors",
            "nb_uniq_active_visitors",
            "nb_engagment_events",
        ]
        datas = Stat.objects.filter(period="day").values("name", "value").annotate(date=Cast("date", CharField()))

        context = super().get_context_data(**kwargs)
        context["stats"] = extract_values_in_list(datas, indicator_names)

        return context


def accessibilite(request):
    return render(request, "pages/accessibilite.html")


def trigger_error(request):
    if request.POST:
        raise Exception("%s error: %s" % (request.POST.get("status_code"), request.POST.get("error_message")))

    print(1 / 0)  # Should raise a ZeroDivisionError.
