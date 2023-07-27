from django.urls import include, path

from lacommunaute.forum_moderation.views import TopicDeleteView


app_name = "forum_moderation_extension"

moderation_urlpatterns = [
    path("topic/<str:slug>-<int:pk>/delete/", TopicDeleteView.as_view(), name="topic_delete"),
]


urlpatterns = [
    path(
        "moderation/",
        include(moderation_urlpatterns),
    ),
]
