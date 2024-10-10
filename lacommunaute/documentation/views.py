from django.conf import settings
from django.contrib.auth.mixins import UserPassesTestMixin
from django.contrib.contenttypes.models import ContentType
from django.db.models import Avg, Count
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.views import View
from django.views.generic import DetailView, ListView
from django.views.generic.edit import CreateView, UpdateView
from taggit.models import Tag

from lacommunaute import documentation
from lacommunaute.documentation.models import Category, Document, DocumentRating
from lacommunaute.forum.models import Forum
from lacommunaute.forum_conversation.forms import PostForm
from lacommunaute.forum_conversation.models import Topic
from lacommunaute.forum_conversation.view_mixins import FilteredTopicsListViewMixin


class CategoryListView(ListView):
    model = Category
    template_name = "documentation/category_list.html"
    context_object_name = "categories"
    paginate_by = 20 * 3


class CategoryDetailView(DetailView):
    model = Category
    context_object_name = "category"

    def get_template_names(self):
        if self.request.META.get("HTTP_HX_REQUEST"):
            return ["documentation/document_list.html"]
        return ["documentation/category_detail.html"]

    def get_active_tag_slug(self):
        if not hasattr(self, "active_tag_slug"):
            self.active_tag_slug = self.request.GET.get("tag") or None
        return self.active_tag_slug

    def get_filtered_documents(self):
        if self.get_active_tag_slug():
            return self.object.documents.filter(tags__slug=self.get_active_tag_slug()).prefetch_related("tags")
        return self.object.documents.all()

    def get_tags_of_documents(self):
        return Tag.objects.filter(
            taggit_taggeditem_items__content_type=ContentType.objects.get_for_model(Document),
            taggit_taggeditem_items__object_id__in=self.object.documents.all().values_list("id", flat=True),
        ).distinct()

    def get_queryset(self):
        return super().get_queryset().prefetch_related("documents__tags")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["tags"] = self.get_tags_of_documents()
        context["active_tag_slug"] = self.get_active_tag_slug()
        context["documents"] = self.get_filtered_documents()
        return context


class RatingMixin:
    def get_sum_and_mean_of_ratings(self, document):
        return DocumentRating.objects.filter(document=document).aggregate(count=Count("rating"), average=Avg("rating"))

    def get_session_rating(self, document):
        return getattr(
            DocumentRating.objects.filter(document=document, session_id=self.request.session.session_key).first(),
            "rating",
            None,
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context = context | {
            "rating": self.get_session_rating(self.object),
            **self.get_sum_and_mean_of_ratings(self.object),
        }
        return context


class DocumentDetailView(FilteredTopicsListViewMixin, RatingMixin, DetailView):
    model = Document
    template_name = "documentation/document_detail.html"
    context_object_name = "document"

    def get_topics(self):
        # needs pagination
        return self.filter_queryset(Topic.objects.filter(document=self.object).optimized_for_topics_list(self.request.user.id))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["topics"] = self.get_topics()
        context["form"] = PostForm(user=self.request.user)

        context["loadmoretopic_url"] = self.get_load_more_url(self.object.get_absolute_url())
        context["filter_dropdown_endpoint"] = (
            None if self.request.GET.get("page") else self.object.get_absolute_url())

        context["loadmoretopic_suffix"] = "topics"
        context["forum"] = Forum.objects.get_main_forum()
        context = context | self.get_topic_filter_context()
        return context


class DocumentRatingView(RatingMixin, View):
    def post(self, request, *args, **kwargs):
        document_rating = DocumentRating.objects.create(
            document=get_object_or_404(Document, pk=self.kwargs["pk"]),
            user=request.user if request.user.is_authenticated else None,
            rating=int(request.POST["rating"]),
            session_id=request.session.session_key,
        )

        return render(
            request,
            "documentation/partials/rating.html",
            context={"rating": document_rating.rating, **self.get_sum_and_mean_of_ratings(document_rating.document)},
        )


# CREATE AND UPDATE VIEWS


class CreateUpdateMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_superuser

    def get_success_url(self):
        return self.object.get_absolute_url()


class CategoryCreateUpdateMixin(CreateUpdateMixin):
    model = Category
    template_name = "documentation/category_create_or_update.html"
    fields = ["name", "short_description", "description", "image"]


class CategoryCreateView(CategoryCreateUpdateMixin, CreateView):
    def get_context_data(self, **kwargs):
        additionnal_context = {
            "title": "Créer une nouvelle catégorie",
            "back_url": reverse("documentation:category_list"),
        }
        return super().get_context_data(**kwargs) | additionnal_context


class CategoryUpdateView(CategoryCreateUpdateMixin, UpdateView):
    def get_context_data(self, **kwargs):
        additionnal_context = {
            "title": f"Modifier la catégorie {self.object.name}",
            "back_url": self.object.get_absolute_url(),
        }
        return super().get_context_data(**kwargs) | additionnal_context
