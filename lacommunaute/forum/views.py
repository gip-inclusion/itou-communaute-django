import logging
from typing import Any

from django.conf import settings
from django.contrib.auth.mixins import UserPassesTestMixin
from django.contrib.auth.models import Group
from django.db.models import Count, Exists, OuterRef
from django.db.models.query import QuerySet
from django.urls import reverse
from django.views.generic import CreateView, ListView
from machina.apps.forum.views import ForumView as BaseForumView
from machina.core.db.models import get_model
from machina.core.loading import get_class

from lacommunaute.forum.models import Forum
from lacommunaute.forum_conversation.forms import PostForm
from lacommunaute.forum_conversation.models import Topic
from lacommunaute.users.models import User


logger = logging.getLogger(__name__)

PermissionRequiredMixin = get_class("forum_permission.viewmixins", "PermissionRequiredMixin")

ForumPermission = get_model("forum_permission", "ForumPermission")
UserForumPermission = get_model("forum_permission", "UserForumPermission")
GroupForumPermission = get_model("forum_permission", "GroupForumPermission")


class ForumView(BaseForumView):
    paginate_by = settings.FORUM_TOPICS_NUMBER_PER_PAGE

    def get_queryset(self):
        forum = self.get_forum()
        qs = forum.topics.optimized_for_topics_list(self.request.user.id)

        return qs

    def get_context_data(self, **kwargs):
        forum = self.get_forum()
        context = super().get_context_data(**kwargs)
        context["FORUM_NUMBER_POSTS_PER_TOPIC"] = settings.FORUM_NUMBER_POSTS_PER_TOPIC
        context["next_url"] = reverse("forum_extension:forum", kwargs={"pk": forum.pk, "slug": self.forum.slug})
        context["loadmoretopic_url"] = reverse(
            "forum_conversation_extension:topic_list", kwargs={"forum_pk": forum.pk, "forum_slug": self.forum.slug}
        )
        context["loadmoretopic_suffix"] = "topicsinforum"
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
        return reverse("forum_conversation_extension:home")


class CategoryForumListView(ListView):
    template_name = "forum/category_forum_list.html"
    context_object_name = "forums"

    def get_queryset(self) -> QuerySet[Any]:
        return Forum.objects.exclude(is_private=True).filter(type=Forum.FORUM_CAT, level=0)
