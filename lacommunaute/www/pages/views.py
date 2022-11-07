import logging

from django.shortcuts import render
from django.views.generic import ListView
from machina.core.db.models import get_model


logger = logging.getLogger(__name__)

Forum = get_model("forum", "Forum")


class HomeListView(ListView):
    template_name = "pages/home.html"
    queryset = Forum.objects.filter(is_highlighted=True)
    context_object_name = "forums"


def contact(request):
    return render(request, "pages/contact.html")


def statistiques(request):
    return render(request, "pages/statistiques.html")


def accessibilite(request):
    return render(request, "pages/accessibilite.html")


def trigger_error(request):
    if request.POST:
        raise Exception("%s error: %s" % (request.POST.get("status_code"), request.POST.get("error_message")))

    print(1 / 0)  # Should raise a ZeroDivisionError.
