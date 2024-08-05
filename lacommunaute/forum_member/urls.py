from django.urls import path

from lacommunaute.forum_member.views import (
    ForumProfileDetailView,
    ForumProfileUpdateView,
    ModeratorProfileListView,
    SeekersListView,
)


app_name = "members"

urlpatterns = [
    path("profile/edit/", ForumProfileUpdateView.as_view(), name="profile_update"),
    path("profile/<str:username>/", ForumProfileDetailView.as_view(), name="profile"),
    path("forum/<str:slug>-<int:pk>/", ModeratorProfileListView.as_view(), name="forum_profiles"),
    path("seekers/", SeekersListView.as_view(), name="seekers"),
]
