from django.urls import path

from lacommunaute.forum_member.views import (
    ForumProfileDetailView,
    ForumProfileUpdateView,
    JoinForumFormView,
    JoinForumLandingView,
    ModeratorProfileListView,
)


app_name = "members"

urlpatterns = [
    path("profile/edit/", ForumProfileUpdateView.as_view(), name="profile_update"),
    path("profile/<str:username>/", ForumProfileDetailView.as_view(), name="profile"),
    path("forum/<str:slug>-<int:pk>/", ModeratorProfileListView.as_view(), name="forum_profiles"),
    path("join-forum-landing/<uuid:token>/", JoinForumLandingView.as_view(), name="join_forum_landing"),
    path("join-forum/<uuid:token>/", JoinForumFormView.as_view(), name="join_forum_form"),
]
