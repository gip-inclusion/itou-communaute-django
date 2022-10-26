import logging

from django.shortcuts import render


logger = logging.getLogger(__name__)


def home(request):
    return render(request, "pages/home.html")


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
