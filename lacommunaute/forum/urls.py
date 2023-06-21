from django.urls import path

from lacommunaute.forum.views import CategoryForumListView, ForumView


app_name = "forum_extension"


urlpatterns = [
    path("forum/<str:slug>-<int:pk>/", ForumView.as_view(), name="forum"),
    path("forum/categories/", CategoryForumListView.as_view(), name="categories"),
]
