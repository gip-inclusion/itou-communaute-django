from django.urls import include, path

from lacommunaute.www.forum_conversation_views.views import (
    PostFeedCreateView,
    PostJobOfferCreateView,
    PostListView,
    TopicContentView,
    TopicJobOfferCreateView,
    TopicLikeView,
)


app_name = "forum_conversation_extension"

conversation_urlpatterns = [
    path("topic/<str:slug>-<int:pk>/like", TopicLikeView.as_view(), name="like_topic"),
    path("topic/<str:slug>-<int:pk>/showmore/topic", TopicContentView.as_view(), name="showmore_topic"),
    path("topic/<str:slug>-<int:pk>/showmore/posts", PostListView.as_view(), name="showmore_posts"),
    path("topic/<str:slug>-<int:pk>/comment", PostFeedCreateView.as_view(), name="post_create"),
    path("joboffer/create/", TopicJobOfferCreateView.as_view(), name="joboffer_create"),
    path(
        "joboffer/<str:topic_slug>-<int:topic_pk>/candidate/",
        PostJobOfferCreateView.as_view(),
        name="joboffer_candidate",
    ),
]

urlpatterns = [
    path(
        "forum/<str:forum_slug>-<int:forum_pk>/",
        include(conversation_urlpatterns),
    ),
]
