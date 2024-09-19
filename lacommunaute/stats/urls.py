from django.urls import path

from lacommunaute.stats.views import (
    DailyDSPView,
    MonthlyVisitorsView,
    StatistiquesPageView,
)


app_name = "stats"

urlpatterns = [
    path("", StatistiquesPageView.as_view(), name="statistiques"),
    path("monthly-visitors/", MonthlyVisitorsView.as_view(), name="monthly_visitors"),
    path("dsp/", DailyDSPView.as_view(), name="dsp"),
    # deactivited until ForumStatWeekArchiveView manages GenericForeignKey and matomo colleciton is updated
    # path("weekly/<int:year>/<int:week>/", ForumStatWeekArchiveView.as_view(), name="forum_stat_week_archive"),
    # path("weekly/", redirect_to_latest_weekly_stats, name="redirect_to_latest_weekly_stats"),
]
