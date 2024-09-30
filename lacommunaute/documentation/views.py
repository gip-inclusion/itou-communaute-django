from django.contrib.auth.mixins import UserPassesTestMixin
from django.contrib.contenttypes.models import ContentType
from django.urls import reverse
from django.views.generic import DetailView, ListView
from django.views.generic.edit import CreateView, UpdateView
from taggit.models import Tag

from lacommunaute.documentation.models import Category, Document


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
        context["active_tag_slug"] = self.request.GET.get("tag") or None
        return context


class DocumentDetailView(DetailView):
    model = Document
    template_name = "documentation/document_detail.html"
    context_object_name = "document"


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
