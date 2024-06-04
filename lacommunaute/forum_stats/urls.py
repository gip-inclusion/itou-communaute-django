from django.urls import path

from lacommunaute.forum_stats.views import StatistiquesPageView


app_name = "forum_stats"

urlpatterns = [path("", StatistiquesPageView.as_view(), name="statistiques")]
