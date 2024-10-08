from django.contrib.sitemaps.views import sitemap
from django.urls import path
from django.views.generic.base import TemplateView

from lacommunaute.pages import sitemaps, views


sitemaps = {
    "pages": sitemaps.PagesSitemap,
    "forum": sitemaps.ForumSitemap,
    "topic": sitemaps.TopicSitemap,
    "partner": sitemaps.PartnerSitemap,
}

app_name = "pages"

urlpatterns = [
    path("", views.HomeView.as_view(), name="home"),
    path("accessibilite/", views.accessibilite, name="accessibilite"),
    path("mentions-legales/", views.mentions_legales, name="mentions_legales"),
    path("politique-de-confidentialite/", views.politique_de_confidentialite, name="politique_de_confidentialite"),
    path("landing-pages/", views.LandingPagesListView.as_view(), name="landing_pages"),
    path("robots.txt", TemplateView.as_view(template_name="robots.txt", content_type="text/plain"), name="robots"),
    path("sitemap.xml", sitemap, {"sitemaps": sitemaps}, name="django.contrib.sitemaps.views.sitemap"),
]
