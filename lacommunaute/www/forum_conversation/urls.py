from django.urls import include, path

from lacommunaute.www.forum_conversation.views import PostListView, TopicLikeView


app_name = "forum_conversation_extension"

conversation_urlpatterns = [
    path("topic/<str:slug>-<int:pk>/like", TopicLikeView.as_view(), name="like_topic"),
    path("topic/<str:slug>-<int:pk>/showmore/posts", PostListView.as_view(), name="showmore_posts"),
]

urlpatterns = [
    path(
        "forum/<str:forum_slug>-<int:forum_pk>/",
        include(conversation_urlpatterns),
    ),
]
