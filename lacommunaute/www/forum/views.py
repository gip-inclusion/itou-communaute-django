from django.contrib.auth.mixins import UserPassesTestMixin
from django.db.models import Count
from django.shortcuts import get_object_or_404
from django.views.generic import DetailView, ListView
from machina.core.db.models import get_model
from machina.core.loading import get_class


Forum = get_model("forum", "Forum")
Topic = get_model("forum_conversation", "Topic")

ForumVisibilityContentTree = get_class("forum.visibility", "ForumVisibilityContentTree")
PermissionRequiredMixin = get_class("forum_permission.viewmixins", "PermissionRequiredMixin")


class ModeratorEngagementView(PermissionRequiredMixin, ListView):
    context_object_name = "topics"
    template_name = "forum/moderator_engagement.html"
    permission_required = ["can_approve_posts"]

    def get_forum(self):
        """Returns the forum to consider."""
        if not hasattr(self, "forum"):
            self.forum = get_object_or_404(Forum, pk=self.kwargs["pk"])
        return self.forum

    def get_queryset(self):
        """Returns the list of items for this view."""
        self.forum = self.get_forum()
        return (
            self.forum.topics.exclude(approved=False)
            .annotate(
                likes=Count("likers", distinct=True),
                views=Count("tracks", distinct=True),
                replies=Count("posts", distinct=True),
                attached=Count("posts__attachments", distinct=True),
                votes=Count("poll__options__votes", distinct=True),
            )
            .order_by("-last_post_on")
        )

    def get_controlled_object(self):
        """Returns the controlled object."""
        return self.get_forum()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["forum"] = self.forum
        return context


class FunnelView(UserPassesTestMixin, DetailView):
    model = Forum
    template_name = "forum/funnel.html"

    def test_func(self):
        return self.request.user.is_staff
