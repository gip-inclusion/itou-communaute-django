from django.urls import path

from lacommunaute.forum_stats.views import MonthlyVisitorsViews, StatistiquesPageView


app_name = "forum_stats"

urlpatterns = [
    path("", StatistiquesPageView.as_view(), name="statistiques"),
    path("monthly_visitors/", MonthlyVisitorsViews.as_view(), name="monthly_visitors"),
]
