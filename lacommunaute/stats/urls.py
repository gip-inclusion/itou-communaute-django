from django.urls import path

from lacommunaute.stats.views import (
    DailyDSPView,
    DocumentStatsView,
    MonthlyVisitorsView,
    StatistiquesPageView,
)


app_name = "stats"

urlpatterns = [
    path("", StatistiquesPageView.as_view(), name="statistiques"),
    path("monthly-visitors/", MonthlyVisitorsView.as_view(), name="monthly_visitors"),
    path("dsp/", DailyDSPView.as_view(), name="dsp"),
    path("documents/", DocumentStatsView.as_view(), name="document_stats"),
]
