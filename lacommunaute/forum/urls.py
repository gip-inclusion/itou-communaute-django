from django.urls import path
from machina.apps.forum.views import IndexView

from lacommunaute.forum.views import (
    CategoryForumCreateView,
    CategoryForumListView,
    ForumRatingView,
    ForumUpdateView,
    ForumView,
    SubCategoryForumCreateView,
)


app_name = "forum_extension"


urlpatterns = [
    path("forum/<str:slug>-<int:pk>/", ForumView.as_view(), name="forum"),
    path("forum/<str:slug>-<int:pk>/update/", ForumUpdateView.as_view(), name="edit_forum"),
    path("forum/<str:slug>-<int:pk>/rate/", ForumRatingView.as_view(), name="rate"),
    path("forums/", IndexView.as_view(), name="index"),
    path("documentation/", CategoryForumListView.as_view(), name="documentation"),
    path("documentation/category/create/", CategoryForumCreateView.as_view(), name="create_category"),
    path("documentation/category/<int:pk>/create/", SubCategoryForumCreateView.as_view(), name="create_subcategory"),
]
