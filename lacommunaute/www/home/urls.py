from django.urls import path

from lacommunaute.www.home import views


# https://docs.djangoproject.com/en/dev/topics/http/urls/#url-namespaces-and-included-urlconfs
app_name = "home"


urlpatterns = [
    path("", views.home, name="hp"),
]
