import logging
from typing import Any

from django.conf import settings
from django.db.models import Count, Exists, OuterRef
from django.db.models.query import QuerySet
from django.urls import reverse
from django.views.generic import ListView
from machina.apps.forum.views import ForumView as BaseForumView
from machina.core.loading import get_class

from lacommunaute.forum.models import Forum
from lacommunaute.forum_conversation.forms import PostForm
from lacommunaute.forum_conversation.models import Topic
from lacommunaute.users.models import User


logger = logging.getLogger(__name__)

PermissionRequiredMixin = get_class("forum_permission.viewmixins", "PermissionRequiredMixin")


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


class CategoryForumListView(ListView):
    template_name = "forum/category_forum_list.html"
    context_object_name = "forums"

    def get_queryset(self) -> QuerySet[Any]:
        return Forum.objects.exclude(is_private=True).filter(type=Forum.FORUM_CAT, level=0)
