import logging

from django.conf import settings
from django.contrib.auth.mixins import UserPassesTestMixin
from django.contrib.auth.models import Group
from django.db.models import Count, Exists, OuterRef
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.views.generic import CreateView, ListView
from machina.apps.forum.views import ForumView as BaseForumView, IndexView as BaseIndexView
from machina.core.db.models import get_model
from machina.core.loading import get_class

from lacommunaute.forum.models import Forum
from lacommunaute.forum_conversation.forms import PostForm
from lacommunaute.forum_conversation.models import Topic
from lacommunaute.users.models import User


logger = logging.getLogger(__name__)

ForumVisibilityContentTree = get_class("forum.visibility", "ForumVisibilityContentTree")
PermissionRequiredMixin = get_class("forum_permission.viewmixins", "PermissionRequiredMixin")

ForumPermission = get_model("forum_permission", "ForumPermission")
UserForumPermission = get_model("forum_permission", "UserForumPermission")
GroupForumPermission = get_model("forum_permission", "GroupForumPermission")


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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["topics"] = (
            Topic.objects.unanswered()
            .filter(forum__in=Forum.objects.public())
            .annotate(likes=Count("likers"))
            .annotate(has_liked=Exists(User.objects.filter(topic_likes=OuterRef("id"), id=self.request.user.id)))
            .select_related("poster", "poster__forum_profile", "first_post", "forum", "certified_post")
            .prefetch_related(
                "poll",
                "poll__options",
                "poll__options__votes",
                "first_post__attachments",
                "first_post__poster",
            )
            .order_by("-last_post_on")
        )
        context["form"] = PostForm(user=self.request.user)

        if self.request.GET.get("new", None):
            context["pending_topics_tab"] = True
        else:
            context["forums_tab"] = True

        return context


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
                "first_post__poster",
                "forum",
                "certified_post",
                "certified_post__post",
                "certified_post__post__poster",
            )
            .prefetch_related(
                "poll",
                "poll__options",
                "poll__options__votes",
                "first_post__attachments",
                "certified_post__post__attachments",
            )
            .order_by("-last_post_on")
        )

        if self.request.GET.get("new", None):
            qs = qs.filter(posts_count=1).exclude(status=Topic.TOPIC_LOCKED)

        return qs

    def get_context_data(self, **kwargs):
        forum = self.get_forum()
        context = super().get_context_data(**kwargs)
        context["FORUM_NUMBER_POSTS_PER_TOPIC"] = settings.FORUM_NUMBER_POSTS_PER_TOPIC
        context["next_url"] = reverse("forum_extension:forum", kwargs={"pk": forum.pk, "slug": self.forum.slug})
        context["form"] = PostForm(forum=forum, user=self.request.user)
        context["announces"] = list(
            self.get_forum()
            .topics.select_related(
                "poster",
                "poster__forum_profile",
                "first_post",
                "first_post__poster",
                "forum",
            )
            .filter(type=Topic.TOPIC_ANNOUNCE)
            .annotate(likes=Count("likers"))
            .annotate(has_liked=Exists(User.objects.filter(topic_likes=OuterRef("id"), id=self.request.user.id)))
        )
        return context


class ForumCreateView(UserPassesTestMixin, CreateView):
    model = Forum
    fields = ["name", "description"]

    def test_func(self):
        return self.request.user.is_superuser

    def form_valid(self, form):
        instance = form.save(commit=False)

        moderators, _ = Group.objects.get_or_create(name=f"{instance.name} moderators")

        instance.type = 0
        instance.is_private = False
        instance.save()

        declined = [
            "can_edit_posts",
            "can_lock_topics",
            "can_delete_posts",
            "can_move_topics",
            "can_approve_posts",
            "can_reply_to_locked_topics",
            "can_attach_file",
            "can_create_polls",
            "can_post_stickies",
            "can_post_announcements",
        ]

        moderators_perms = [
            GroupForumPermission(group=moderators, permission=permission, has_perm=True, forum=instance)
            for permission in ForumPermission.objects.all()
        ]
        GroupForumPermission.objects.bulk_create(moderators_perms)

        anonymous_declined_perms = [
            UserForumPermission(
                anonymous_user=True,
                authenticated_user=False,
                permission=permission,
                has_perm=False,
                forum=instance,
            )
            for permission in ForumPermission.objects.filter(codename__in=declined)
        ]
        anonymous_authorized_perms = [
            UserForumPermission(
                anonymous_user=True, authenticated_user=False, permission=permission, has_perm=True, forum=instance
            )
            for permission in ForumPermission.objects.exclude(codename__in=declined)
        ]
        authentified_declined_perms = [
            UserForumPermission(
                anonymous_user=False,
                authenticated_user=True,
                permission=permission,
                has_perm=False,
                forum=instance,
            )
            for permission in ForumPermission.objects.filter(codename__in=declined)
        ]

        authentified_authorized_perms = [
            UserForumPermission(
                anonymous_user=False, authenticated_user=True, permission=permission, has_perm=True, forum=instance
            )
            for permission in ForumPermission.objects.exclude(codename__in=declined)
        ]

        UserForumPermission.objects.bulk_create(
            anonymous_declined_perms
            + anonymous_authorized_perms
            + authentified_declined_perms
            + authentified_authorized_perms
        )

        return super().form_valid(form)

    def get_success_url(self):
        return reverse("forum_extension:home")


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
