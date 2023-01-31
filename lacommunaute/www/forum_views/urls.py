from django.urls import path

from lacommunaute.www.forum_views.views import ForumView, FunnelView, IndexView, ModeratorEngagementView


app_name = "forum_extension"


urlpatterns = [
    path("", IndexView.as_view(), name="home"),
    path("forum/<str:slug>-<int:pk>/", ForumView.as_view(), name="forum"),
    path("forum/<str:slug>-<int:pk>/engagement", ModeratorEngagementView.as_view(), name="engagement"),
    path("forum/<str:slug>-<int:pk>/funnel", FunnelView.as_view(), name="funnel"),
]
