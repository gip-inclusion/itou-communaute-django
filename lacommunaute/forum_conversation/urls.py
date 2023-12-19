from django.urls import include, path

from lacommunaute.forum_conversation.views import NewsFeedTopicListView, TopicListView
from lacommunaute.forum_conversation.views_htmx import (
    CertifiedPostView,
    ForumTopicListView,
    PostFeedCreateView,
    PostListView,
    TopicCertifiedPostView,
    TopicContentView,
)


app_name = "forum_conversation_extension"

conversation_urlpatterns = [
    path("topic/<str:slug>-<int:pk>/showmore/topic", TopicContentView.as_view(), name="showmore_topic"),
    path("topic/<str:slug>-<int:pk>/showmore/posts", PostListView.as_view(), name="showmore_posts"),
    path("topic/<str:slug>-<int:pk>/showmore/certified", TopicCertifiedPostView.as_view(), name="showmore_certified"),
    path("topic/<str:slug>-<int:pk>/comment", PostFeedCreateView.as_view(), name="post_create"),
    path("topic/<str:slug>-<int:pk>/certify", CertifiedPostView.as_view(), name="certify"),
    path("topic/", ForumTopicListView.as_view(), name="topic_list"),
]


urlpatterns = [
    path("topics/", TopicListView.as_view(), name="topics"),
    path("news/", NewsFeedTopicListView.as_view(), name="newsfeed"),
    path(
        "forum/<str:forum_slug>-<int:forum_pk>/",
        include(conversation_urlpatterns),
    ),
]
