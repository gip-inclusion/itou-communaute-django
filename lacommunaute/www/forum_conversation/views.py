import logging

from django.shortcuts import get_object_or_404, render
from django.views import View
from machina.core.db.models import get_model
from machina.core.loading import get_class


logger = logging.getLogger(__name__)

Topic = get_model("forum_conversation", "Topic")
Post = get_model("forum_conversation", "Post")
PermissionRequiredMixin = get_class("forum_permission.viewmixins", "PermissionRequiredMixin")
TrackingHandler = get_class("forum_tracking.handler", "TrackingHandler")

track_handler = TrackingHandler()


class TopicLikeView(PermissionRequiredMixin, View):
    permission_required = [
        "can_read_forum",
    ]

    def get_topic(self):
        if not hasattr(self, "topic"):
            self.topic = get_object_or_404(
                Topic.objects.select_related("forum").all(),
                pk=self.kwargs["pk"],
            )
        return self.topic

    def post(self, request, **kwargs):
        topic = self.get_topic()

        if not topic.likers.filter(id=request.user.id).exists():
            topic.likers.add(request.user)
            topic.has_liked = True
        else:
            topic.likers.remove(request.user)
            topic.has_liked = False

        topic.save()
        topic.likes = topic.likers.count()

        track_handler.mark_topic_read(topic, request.user)

        return render(request, "forum_conversation/partials/topic_likes.html", context={"topic": topic})

    def get_controlled_object(self):
        return self.get_topic().forum


class TopicContentView(PermissionRequiredMixin, View):
    permission_required = [
        "can_read_forum",
    ]

    def get_topic(self):
        if not hasattr(self, "topic"):
            self.topic = get_object_or_404(
                Topic.objects.select_related("forum").all(),
                pk=self.kwargs["pk"],
            )
        return self.topic

    def get(self, request, **kwargs):
        topic = self.get_topic()

        track_handler.mark_topic_read(topic, request.user)

        return render(
            request,
            "forum_conversation/partials/topic_content.html",
            context={"topic": topic},
        )

    def get_controlled_object(self):
        return self.get_topic().forum


class PostListView(PermissionRequiredMixin, View):
    permission_required = [
        "can_read_forum",
    ]

    def get_topic(self):
        if not hasattr(self, "topic"):
            self.topic = get_object_or_404(
                Topic.objects.select_related("forum").all(),
                pk=self.kwargs["pk"],
            )
        return self.topic

    def get(self, request, **kwargs):
        topic = self.get_topic()
        posts = (
            Post.objects.exclude(topic__type=Topic.TOPIC_ANNOUNCE)
            .exclude(topic__approved=False)
            .exclude(pk=topic.first_post.pk)
            .filter(topic=topic)
            .order_by("created")
            .select_related("poster", "poster__forum_profile")
            .prefetch_related("attachments")
        )

        track_handler.mark_topic_read(topic, request.user)

        return render(request, "forum_conversation/partials/posts_list.html", context={"topic": topic, "posts": posts})

    def get_controlled_object(self):
        return self.get_topic().forum
