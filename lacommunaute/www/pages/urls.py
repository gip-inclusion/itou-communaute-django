from django.urls import path

from lacommunaute.www.pages import views


app_name = "pages"

urlpatterns = [
    path("", views.HomeListView.as_view(), name="home"),
    path("contact/", views.contact, name="contact"),
    path("statistiques/", views.StatistiquesPageView.as_view(), name="statistiques"),
    path("accessibilite/", views.accessibilite, name="accessibilite"),
    path("sentry-debug/", views.trigger_error, name="sentry_debug"),
]
