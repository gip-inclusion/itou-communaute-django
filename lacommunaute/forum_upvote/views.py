import logging

from django.contrib.contenttypes.models import ContentType
from django.shortcuts import get_object_or_404, render
from django.views import View
from machina.core.loading import get_class

from lacommunaute.forum_conversation.models import Post
from lacommunaute.forum_upvote.models import UpVote


logger = logging.getLogger(__name__)

PermissionRequiredMixin = get_class("forum_permission.viewmixins", "PermissionRequiredMixin")
TrackingHandler = get_class("forum_tracking.handler", "TrackingHandler")

track_handler = TrackingHandler()


class PostUpvoteView(PermissionRequiredMixin, View):
    def dispatch(self, request, *args, **kwargs):
        if request.method != "POST":
            return self.http_method_not_allowed(request)
        return super().dispatch(request, *args, **kwargs)

    def get_object(self):
        if not hasattr(self, "object"):
            self.object = get_object_or_404(
                Post.objects.select_related("topic__forum").all(),
                pk=self.request.POST["post_pk"],
                topic__pk=self.request.POST["pk"],
            )
        return self.object

    def post(self, request, **kwargs):
        post = self.get_object()
        upvote = UpVote.objects.filter(
            voter_id=request.user.id,
            object_id=post.id,
            content_type=ContentType.objects.get_for_model(post),
        )

        if upvote.exists():
            upvote.delete()
            post.has_upvoted = False
        else:
            UpVote(
                voter_id=request.user.id,
                object_id=post.id,
                content_type=ContentType.objects.get_for_model(post),
            ).save()
            post.has_upvoted = True

        post.upvotes_count = post.upvotes.count()

        track_handler.mark_topic_read(post.topic, request.user)

        return render(request, "forum_conversation/partials/post_upvotes.html", context={"post": post})

    def get_controlled_object(self):
        return self.get_object().topic.forum

    def perform_permissions_check(self, user, obj, perms):
        return self.request.forum_permission_handler.can_read_forum(obj, user)
