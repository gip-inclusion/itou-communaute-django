from django.urls import path

from lacommunaute.www.forum.views import FunnelView, ModeratorEngagementView


app_name = "forum_extension"


urlpatterns = [
    path("forum/<str:slug>-<int:pk>/engagement", ModeratorEngagementView.as_view(), name="engagement"),
    path("forum/<str:slug>-<int:pk>/funnel", FunnelView.as_view(), name="funnel"),
]
