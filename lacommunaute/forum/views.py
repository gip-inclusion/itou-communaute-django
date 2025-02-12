import logging

from django.conf import settings
from django.contrib.auth.mixins import UserPassesTestMixin
from django.contrib.contenttypes.models import ContentType
from django.db.models.query import QuerySet
from django.shortcuts import get_object_or_404, render
from django.urls import reverse, reverse_lazy
from django.views import View
from django.views.generic import CreateView, ListView, UpdateView
from machina.apps.forum.views import ForumView as BaseForumView
from machina.core.loading import get_class
from taggit.models import Tag

from lacommunaute.forum.forms import ForumForm
from lacommunaute.forum.models import Forum, ForumRating
from lacommunaute.forum_conversation.forms import PostForm
from lacommunaute.forum_conversation.view_mixins import FilteredTopicsListViewMixin
from lacommunaute.forum_upvote.models import UpVote
from lacommunaute.utils.perms import add_public_perms_on_forum, forum_visibility_content_tree_from_forums


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

        context["rating"] = forum.get_session_rating(self.request.session.session_key)

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
        return self.request.user.is_staff

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = f"Mettre à jour le forum {self.object.name}"
        context["back_url"] = reverse("forum_extension:forum", kwargs={"pk": self.object.pk, "slug": self.object.slug})
        return context


class CategoryForumListView(ListView):
    template_name = "forum/category_forum_list.html"
    context_object_name = "forums"

    def get_queryset(self) -> QuerySet[Forum]:
        return Forum.objects.filter(type=Forum.FORUM_CAT, level=0)


class BaseCategoryForumCreateView(UserPassesTestMixin, CreateView):
    template_name = "forum/forum_create_or_update.html"
    form_class = ForumForm

    def test_func(self):
        return self.request.user.is_staff

    def form_valid(self, form):
        response = super().form_valid(form)
        add_public_perms_on_forum(form.instance)
        return response


class CategoryForumCreateView(BaseCategoryForumCreateView):
    success_url = reverse_lazy("forum_extension:documentation")

    def form_valid(self, form):
        form.instance.parent = None
        form.instance.type = Forum.FORUM_CAT
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Créer une nouvelle catégorie documentaire"
        context["back_url"] = reverse("forum_extension:documentation")
        return context


class SubCategoryForumCreateView(BaseCategoryForumCreateView):
    def get_success_url(self):
        return reverse("forum_extension:forum", kwargs={"pk": self.object.pk, "slug": self.object.slug})

    def get_parent_forum(self):
        return Forum.objects.get(pk=self.kwargs["pk"])

    def form_valid(self, form):
        form.instance.type = Forum.FORUM_POST
        form.instance.parent = self.get_parent_forum()
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = f"Créer une fiche pratique dans la catégorie {self.get_parent_forum().name}"
        context["back_url"] = reverse(
            "forum_extension:forum", kwargs={"pk": self.get_parent_forum().pk, "slug": self.get_parent_forum().slug}
        )
        return context


class ForumRatingView(View):
    def post(self, request, *args, **kwargs):
        forum_rating = ForumRating.objects.create(
            forum=get_object_or_404(Forum, pk=self.kwargs["pk"]),
            user=request.user if request.user.is_authenticated else None,
            rating=int(request.POST["rating"]),
            session_id=request.session.session_key,
        )

        return render(
            request,
            "forum/partials/rating.html",
            context={"forum": forum_rating.forum, "rating": forum_rating.rating},
        )
