import logging

from django.conf import settings
from django.contrib.auth.mixins import UserPassesTestMixin
from django.db.models import Count, Exists, OuterRef
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.views.generic import DetailView, ListView
from machina.apps.forum.views import ForumView as BaseForumView, IndexView as BaseIndexView
from machina.core.loading import get_class

from lacommunaute.forum.models import Forum
from lacommunaute.forum_conversation.forms import PostForm
from lacommunaute.forum_conversation.models import Topic
from lacommunaute.users.models import User


logger = logging.getLogger(__name__)

ForumVisibilityContentTree = get_class("forum.visibility", "ForumVisibilityContentTree")
PermissionRequiredMixin = get_class("forum_permission.viewmixins", "PermissionRequiredMixin")


class IndexView(BaseIndexView):
    template_name = "pages/home.html"

    def get_queryset(self):
        """Returns the list of items for this view."""
        return ForumVisibilityContentTree.from_forums(
            self.request.forum_permission_handler.forum_list_filter(
                Forum.objects.all().prefetch_related("members_group__user_set"),
                self.request.user,
            ),
        )


class ForumView(BaseForumView):
    paginate_by = settings.FORUM_TOPICS_NUMBER_PER_PAGE

    def get_queryset(self):
        forum = self.get_forum()
        qs = (
            forum.topics.exclude(type=Topic.TOPIC_ANNOUNCE)
            .exclude(approved=False)
            .annotate(likes=Count("likers"))
            .annotate(has_liked=Exists(User.objects.filter(topic_likes=OuterRef("id"), id=self.request.user.id)))
            .select_related(
                "poster",
                "poster__forum_profile",
                "first_post",
                "forum",
            )
            .prefetch_related(
                "poll",
                "poll__options",
                "poll__options__votes",
                "first_post__attachments",
                "first_post__poster",
            )
            .order_by("-last_post_on")
        )
        return qs

    def get_context_data(self, **kwargs):
        forum = self.get_forum()
        context = super().get_context_data(**kwargs)
        context["FORUM_NUMBER_POSTS_PER_TOPIC"] = settings.FORUM_NUMBER_POSTS_PER_TOPIC
        context["next_url"] = reverse("forum_extension:forum", kwargs={"pk": forum.pk, "slug": self.forum.slug})
        context["form"] = PostForm(forum=forum, user=self.request.user)
        return context


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
        return (
            self.get_forum()
            .topics.exclude(approved=False)
            .annotate(
                likes=Count("likers", distinct=True),
                views=Count("tracks", distinct=True),
                messages=Count("posts", distinct=True),
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
        context["stats"] = self.forum.get_stats(7)
        return context


class FunnelView(UserPassesTestMixin, DetailView):
    model = Forum
    template_name = "forum/funnel.html"

    def test_func(self):
        return self.request.user.is_staff
