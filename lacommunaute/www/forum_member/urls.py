from django.urls import path

from lacommunaute.www.forum_member.views import ForumProfileListView, JoinForumFormView, JoinForumLandingView


app_name = "members"

urlpatterns = [
    path("", ForumProfileListView.as_view(), name="profiles"),
    path("join-forum-landing/", JoinForumLandingView.as_view(), name="join_forum_landing"),
    path("join-forum/", JoinForumFormView.as_view(), name="join_forum_form"),
]
