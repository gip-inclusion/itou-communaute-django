import logging

from django.conf import settings
from django.contrib.auth.mixins import UserPassesTestMixin
from django.contrib.contenttypes.models import ContentType
from django.urls import reverse
from django.views.generic import UpdateView
from machina.apps.forum.views import ForumView as BaseForumView
from machina.core.loading import get_class
from taggit.models import Tag

from lacommunaute.forum.forms import ForumForm
from lacommunaute.forum.models import Forum
from lacommunaute.forum_conversation.forms import PostForm
from lacommunaute.forum_conversation.view_mixins import FilteredTopicsListViewMixin
from lacommunaute.forum_upvote.models import UpVote
from lacommunaute.utils.perms import forum_visibility_content_tree_from_forums


logger = logging.getLogger(__name__)

PermissionRequiredMixin = get_class("forum_permission.viewmixins", "PermissionRequiredMixin")


class SubCategoryForumListMixin:
    def get_descendants(self):
        qs = self.get_forum().get_descendants()

        forum_tag = self.request.GET.get("forum_tag") or None
        if forum_tag:
            qs = qs.filter(tags__slug=forum_tag)

        return qs.prefetch_related("tags")

    def get_tags_of_descendants(self):
        return Tag.objects.filter(
            taggit_taggeditem_items__content_type=ContentType.objects.get_for_model(Forum),
            taggit_taggeditem_items__object_id__in=self.get_forum().get_descendants().values_list("id", flat=True),
        ).distinct()

    def forum_tag_context(self):
        return {
            # TODO : remove permission management, though all forums are public in our case
            "sub_forums": forum_visibility_content_tree_from_forums(self.request, self.get_descendants()),
            "tags_of_descendants": self.get_tags_of_descendants(),
            "active_forum_tag_slug": self.request.GET.get("forum_tag") or None,
        }


class ForumView(BaseForumView, FilteredTopicsListViewMixin, SubCategoryForumListMixin):
    paginate_by = settings.FORUM_TOPICS_NUMBER_PER_PAGE

    def get_template_names(self):
        if self.request.META.get("HTTP_HX_REQUEST"):
            return ["forum_conversation/topic_list.html"]
        if self.will_render_documentation_variant():
            return ["forum/forum_documentation.html"]
        if self.will_render_documentation_category_variant():
            return ["forum/forum_documentation_category.html"]
        return ["forum/forum_detail.html"]

    def will_render_documentation_variant(self):
        return self.get_forum().parent and self.forum.is_in_documentation_area

    def will_render_documentation_category_variant(self):
        return self.get_forum().is_in_documentation_area and self.forum.level == 0

    def get_queryset(self):
        return self.filter_queryset(self.get_forum().topics.optimized_for_topics_list(self.request.user.id))

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
        context["loadmoretopic_url"] = self.get_load_more_url(
            reverse("forum_extension:forum", kwargs={"pk": forum.pk, "slug": self.forum.slug})
        )
        context["loadmoretopic_suffix"] = "topicsinforum"
        context["form"] = PostForm(forum=forum, user=self.request.user)

        context["filter_dropdown_endpoint"] = (
            None
            if self.request.GET.get("page")
            else reverse("forum_extension:forum", kwargs={"pk": forum.pk, "slug": self.forum.slug})
        )
        context = context | self.get_topic_filter_context()

        if self.will_render_documentation_category_variant():
            context = context | self.forum_tag_context()

        if self.will_render_documentation_variant():
            context["sibling_forums"] = forum.get_siblings(include_self=True)

        if forum.image:
            context["og_image"] = forum.image
        return context


class SubCategoryForumListView(BaseForumView, SubCategoryForumListMixin):
    template_name = "forum/partials/subcategory_forum_list.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs) | self.forum_tag_context()
        return context


class ForumUpdateView(UserPassesTestMixin, UpdateView):
    template_name = "forum/forum_create_or_update.html"
    form_class = ForumForm
    model = Forum

    def test_func(self):
        return self.request.user.is_superuser

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = f"Mettre à jour le forum {self.object.name}"
        context["back_url"] = reverse("forum_extension:forum", kwargs={"pk": self.object.pk, "slug": self.object.slug})
        return context
