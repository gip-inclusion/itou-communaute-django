import logging

from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.db.models import Count, Exists, OuterRef
from django.db.models.query import QuerySet
from django.urls import reverse
from django.views.generic import ListView
from machina.apps.forum.views import ForumView as BaseForumView
from machina.core.loading import get_class

from lacommunaute.forum.enums import Kind as ForumKind
from lacommunaute.forum.models import Forum
from lacommunaute.forum_conversation.forms import PostForm
from lacommunaute.forum_conversation.models import Topic
from lacommunaute.forum_upvote.models import UpVote
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

        if self.request.user.is_authenticated:
            forum.has_upvoted = UpVote.objects.filter(
                object_id=forum.id,
                voter=self.request.user,
                content_type_id=ContentType.objects.get_for_model(forum).id,
            ).exists()

        context = super().get_context_data(**kwargs)
        context["forum"] = forum
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
        if forum.parent and forum.parent.type == Forum.FORUM_CAT:
            context["forums"] = Forum.objects.filter(parent=forum.parent).order_by("lft")
            context["parent_forum"] = forum.parent
        return context


class CategoryForumListView(ListView):
    template_name = "forum/category_forum_list.html"
    context_object_name = "forums"

    def get_queryset(self) -> QuerySet[Forum]:
        return Forum.objects.filter(type=Forum.FORUM_CAT, kind=ForumKind.PUBLIC_FORUM, level=0)
