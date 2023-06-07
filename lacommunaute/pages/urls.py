from django.urls import path
from django.views.generic.base import TemplateView

from lacommunaute.pages import views


app_name = "pages"

urlpatterns = [
    path("contact/", views.contact, name="contact"),
    path("statistiques/", views.StatistiquesPageView.as_view(), name="statistiques"),
    path("accessibilite/", views.accessibilite, name="accessibilite"),
    path("landing-pages/", views.LandingPagesListView.as_view(), name="landing_pages"),
    path("sentry-debug/", views.trigger_error, name="sentry_debug"),
    path("robots.txt", TemplateView.as_view(template_name="robots.txt", content_type="text/plain"), name="robots"),
]
