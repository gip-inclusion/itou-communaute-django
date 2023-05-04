from django.urls import path

from lacommunaute.forum_upvote.views import CertifiedPostView, PostUpvoteView


app_name = "forum_upvote"


urlpatterns = [
    path("upvote/", PostUpvoteView.as_view(), name="upvote"),
    path("certify/", CertifiedPostView.as_view(), name="certify"),
]
