from django.http import HttpResponse


def home(request):
    return HttpResponse("Bienvenue sur la communauté de l'inclusion")
