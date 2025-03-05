from logging import getLogger

from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.contenttypes.models import ContentType
from django.shortcuts import get_object_or_404, render
from django.views import View
from django.views.generic import ListView
from machina.core.loading import get_class

from lacommunaute.forum.models import Forum
from lacommunaute.forum_conversation.models import Post
from lacommunaute.forum_upvote.models import UpVote


logger = getLogger("lacommunaute")

PermissionRequiredMixin = get_class("forum_permission.viewmixins", "PermissionRequiredMixin")
TrackingHandler = get_class("forum_tracking.handler", "TrackingHandler")

track_handler = TrackingHandler()


class BaseUpvoteMixin:
    def dispatch(self, request, *args, **kwargs):
        if request.method != "POST":
            return self.http_method_not_allowed(request)
        return super().dispatch(request, *args, **kwargs)

    def perform_permissions_check(self, user, obj, perms):
        return self.request.forum_permission_handler.can_read_forum(obj, user)

    def post(self, request, **kwargs):
        self.object = self.get_object()
        content_type = ContentType.objects.get_for_model(self.object)
        upvote = UpVote.objects.filter(
            voter_id=request.user.id,
            object_id=self.object.id,
            content_type=content_type,
        )

        if upvote.exists():
            upvote.delete()
            self.object.has_upvoted = False
        else:
            UpVote(
                voter_id=request.user.id,
                object_id=self.object.id,
                content_type=content_type,
            ).save()
            self.object.has_upvoted = True

        self.object.upvotes_count = self.object.upvotes.count()

        self.handle_extra_logic(request)

        return render(
            request, "partials/upvotes.html", context={"obj": self.object, "kind": self.object._meta.model_name}
        )

    def handle_extra_logic(self, request):
        raise NotImplementedError("handle_extra_logic method must be implemented in the subclass")


class PostUpvoteView(BaseUpvoteMixin, PermissionRequiredMixin, View):
    def get_object(self):
        if not hasattr(self, "object"):
            self.object = get_object_or_404(
                Post.objects.select_related("topic", "topic__forum").all(),
                pk=self.request.POST["pk"],
            )
        return self.object

    def handle_extra_logic(self, request):
        track_handler.mark_topic_read(self.get_object().topic, request.user)

    def get_controlled_object(self):
        return self.get_object().topic.forum


class ForumUpVoteView(BaseUpvoteMixin, PermissionRequiredMixin, View):
    def get_object(self):
        if not hasattr(self, "object"):
            self.object = get_object_or_404(
                Forum,
                pk=self.request.POST["pk"],
            )
        return self.object

    def handle_extra_logic(self, request):
        track_handler.mark_forums_read([self.get_object()], request.user)

    def get_controlled_object(self):
        return self.get_object()


class UpVoteListView(LoginRequiredMixin, ListView):
    paginate_by = settings.FORUM_TOPICS_NUMBER_PER_PAGE
    template_name = "forum_upvote/upvote_list.html"
    context_object_name = "upvotes"

    def get_queryset(self):
        qs = (
            UpVote.objects.filter(voter=self.request.user)
            .select_related("content_type")
            .prefetch_related("content_object")
            .order_by("-created_at")
        )
        return qs
