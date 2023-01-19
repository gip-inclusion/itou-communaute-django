from django.urls import path

from lacommunaute.www.forum_upvote_views.views import PostUpvoteView


app_name = "forum_upvote"


urlpatterns = [
    path("upvote", PostUpvoteView.as_view(), name="upvote"),
]
