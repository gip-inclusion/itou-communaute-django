from django.urls import path

from lacommunaute.www.forum_member.views import (
    ForumProfileListView,
    JoinForumFormView,
    JoinForumLandingView,
    ModeratorProfileListView,
)


app_name = "members"

urlpatterns = [
    path("", ForumProfileListView.as_view(), name="profiles"),
    path("forum/<str:slug>-<int:pk>/", ModeratorProfileListView.as_view(), name="forum_profiles"),
    path("join-forum-landing/<uuid:token>/", JoinForumLandingView.as_view(), name="join_forum_landing"),
    path("join-forum/<uuid:token>/", JoinForumFormView.as_view(), name="join_forum_form"),
]
