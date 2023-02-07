import logging

from django.shortcuts import render
from django.views.generic.base import TemplateView

from lacommunaute.utils.json import extract_values_in_list, get_json_data


logger = logging.getLogger(__name__)


def contact(request):
    return render(request, "pages/contact.html")


class StatistiquesPageView(TemplateView):
    template_name = "pages/statistiques.html"

    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)
        context["stats"] = extract_values_in_list(get_json_data("./exports/stats_day.json"))
        return context


def accessibilite(request):
    return render(request, "pages/accessibilite.html")


def trigger_error(request):
    if request.POST:
        raise Exception("%s error: %s" % (request.POST.get("status_code"), request.POST.get("error_message")))

    print(1 / 0)  # Should raise a ZeroDivisionError.
