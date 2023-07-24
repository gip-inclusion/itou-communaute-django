from django.urls import path

from lacommunaute.forum_upvote.views import PostUpvoteView


app_name = "forum_upvote"


urlpatterns = [
    path("upvote/post/", PostUpvoteView.as_view(), name="post"),
]
