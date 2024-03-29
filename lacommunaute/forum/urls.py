from django.urls import path
from machina.apps.forum.views import IndexView

from lacommunaute.forum.views import CategoryForumListView, ForumView


app_name = "forum_extension"


urlpatterns = [
    path("forum/<str:slug>-<int:pk>/", ForumView.as_view(), name="forum"),
    path("forums/", IndexView.as_view(), name="index"),
    path("documentation/", CategoryForumListView.as_view(), name="documentation"),
]
