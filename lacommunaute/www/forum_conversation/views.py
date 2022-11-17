import logging

from django.shortcuts import get_object_or_404, render
from django.views import View
from machina.core.db.models import get_model
from machina.core.loading import get_class


logger = logging.getLogger(__name__)

Topic = get_model("forum_conversation", "Topic")
PermissionRequiredMixin = get_class("forum_permission.viewmixins", "PermissionRequiredMixin")


class TopicLikeView(PermissionRequiredMixin, View):
    permission_required = [
        "can_read_forum",
    ]

    def get_topic(self):
        """Returns the topic to consider."""
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

        return render(request, "forum_conversation/partials/topic_likes.html", context={"topic": topic})

    def get_controlled_object(self):
        """Returns the controlled object."""
        return self.get_topic().forum
