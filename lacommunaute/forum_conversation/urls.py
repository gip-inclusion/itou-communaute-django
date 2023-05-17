from django.urls import include, path

from lacommunaute.forum_conversation.views_htmx import (
    ForumTopicListView,
    PostFeedCreateView,
    PostListView,
    TopicCertifiedListView,
    TopicCertifiedPostView,
    TopicContentView,
    TopicLikeView,
    TopicNewsListView,
)


app_name = "forum_conversation_extension"

conversation_urlpatterns = [
    path("topic/<str:slug>-<int:pk>/like", TopicLikeView.as_view(), name="like_topic"),
    path("topic/<str:slug>-<int:pk>/showmore/topic", TopicContentView.as_view(), name="showmore_topic"),
    path("topic/<str:slug>-<int:pk>/showmore/posts", PostListView.as_view(), name="showmore_posts"),
    path("topic/<str:slug>-<int:pk>/showmore/certified", TopicCertifiedPostView.as_view(), name="showmore_certified"),
    path("topic/<str:slug>-<int:pk>/comment", PostFeedCreateView.as_view(), name="post_create"),
    path("topic/", ForumTopicListView.as_view(), name="topic_list"),
]

public_topics_urlpatterns = [
    path("topic/certified/", TopicCertifiedListView.as_view(), name="public_certified_topics_list"),
    path("topic/newsfeed/", TopicNewsListView.as_view(), name="newsfeed_topics_list"),
]

urlpatterns = [
    path(
        "forum/<str:forum_slug>-<int:forum_pk>/",
        include(conversation_urlpatterns),
    ),
    path(
        "public/",
        include(public_topics_urlpatterns),
    ),
]
