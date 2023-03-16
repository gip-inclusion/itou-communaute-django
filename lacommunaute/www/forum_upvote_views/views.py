import logging

from django.shortcuts import get_object_or_404, render
from django.views import View
from machina.core.loading import get_class

from lacommunaute.forum_conversation.forms import PostForm
from lacommunaute.forum_conversation.models import Post
from lacommunaute.forum_conversation.shortcuts import get_posts_of_a_topic_except_first_one
from lacommunaute.forum_upvote.models import CertifiedPost, UpVote
from lacommunaute.forum_upvote.shortcuts import can_certify_post


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
        upvote = UpVote.objects.filter(voter_id=request.user.id, post_id=post.id)

        if upvote.exists():
            upvote.delete()
            post.has_upvoted = False
        else:
            UpVote(voter_id=request.user.id, post_id=post.id).save()
            post.has_upvoted = True

        post.upvotes_count = post.upvotes.count()

        track_handler.mark_topic_read(post.topic, request.user)

        return render(request, "forum_conversation/partials/post_upvotes.html", context={"post": post})

    def get_controlled_object(self):
        return self.get_object().topic.forum

    def perform_permissions_check(self, user, obj, perms):
        return self.request.forum_permission_handler.can_read_forum(obj, user)


class CertifiedPostView(PermissionRequiredMixin, View):
    def _can_certify_post(self, forum, user):
        if not hasattr(self, "can_certify_post"):
            self.can_certify_post = can_certify_post(forum, user)
        return self.can_certify_post

    def dispatch(self, request, *args, **kwargs):
        if request.method != "POST":
            return self.http_method_not_allowed(request)
        return super().dispatch(request, *args, **kwargs)

    def get_object(self):
        if not hasattr(self, "object"):
            self.object = get_object_or_404(
                Post,
                pk=self.request.POST["post_pk"],
            )
        return self.object

    def post(self, request, **kwargs):
        post = self.get_object()
        certified_post = CertifiedPost.objects.filter(post=post)

        if certified_post.exists():
            certified_post.delete()
        else:
            CertifiedPost(post=post, topic=post.topic, user=request.user).save()

        track_handler.mark_topic_read(post.topic, request.user)

        return render(
            request,
            "forum_conversation/partials/posts_list.html",
            context={
                "topic": post.topic,
                "posts": get_posts_of_a_topic_except_first_one(post.topic, request.user),
                "form": PostForm(forum=post.topic.forum, user=request.user),
                "next_url": post.topic.get_absolute_url(),
                "can_certify_post": self._can_certify_post(post.topic.forum, request.user),
            },
        )

    def get_controlled_object(self):
        return self.get_object().topic.forum

    def perform_permissions_check(self, user, obj, perms):
        return self.request.forum_permission_handler.can_read_forum(obj, user) and self._can_certify_post(obj, user)
