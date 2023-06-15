from django.urls import path

from lacommunaute.forum.views import CategoryForumListView, ForumCreateView, ForumView


app_name = "forum_extension"


urlpatterns = [
    path("forum/create/", ForumCreateView.as_view(), name="create"),
    path("forum/<str:slug>-<int:pk>/", ForumView.as_view(), name="forum"),
    path("forum/categories/", CategoryForumListView.as_view(), name="categories"),
]
