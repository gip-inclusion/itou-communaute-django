from django.urls import include, path

from lacommunaute.www.forum_conversation_views.forum_polls.views import TopicPollVoteView


app_name = "forum_polls_extension"

conversation_urlpatterns = [
    path("poll/<int:pk>/vote/", TopicPollVoteView.as_view(), name="topic_poll_vote"),
]

urlpatterns = [
    path(
        "forum/<str:forum_slug>-<int:forum_pk>/",
        include(conversation_urlpatterns),
    ),
]
