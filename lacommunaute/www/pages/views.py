from django.shortcuts import render


def home(request):
    return render(request, "pages/home.html")


def contact(request):
    return render(request, "pages/contact.html")


def statistiques(request):
    return render(request, "pages/statistiques.html")


def accessibilite(request):
    return render(request, "pages/accessibilite.html")
