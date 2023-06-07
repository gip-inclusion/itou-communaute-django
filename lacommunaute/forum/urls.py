from django.urls import path

from lacommunaute.forum.views import ForumCreateView, ForumView, ModeratorEngagementView


app_name = "forum_extension"


urlpatterns = [
    path("forum/create/", ForumCreateView.as_view(), name="create"),
    path("forum/<str:slug>-<int:pk>/", ForumView.as_view(), name="forum"),
    path("forum/<str:slug>-<int:pk>/engagement", ModeratorEngagementView.as_view(), name="engagement"),
]
