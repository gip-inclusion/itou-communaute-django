from django.contrib.auth.mixins import UserPassesTestMixin
from django.contrib.contenttypes.models import ContentType
from django.urls import reverse
from django.views.generic import DetailView, ListView
from django.views.generic.edit import CreateView, UpdateView
from taggit.models import Tag

from lacommunaute.documentation.forms import CategoryForm
from lacommunaute.documentation.models import Category, Document


class CategoryListView(ListView):
    model = Category
    template_name = "documentation/category_list.html"
    context_object_name = "categories"
    paginate_by = 20 * 3


class CategoryDetailView(DetailView):
    model = Category
    template_name = "documentation/category_detail.html"
    context_object_name = "category"

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


class CategoryCreateView(UserPassesTestMixin, CreateView):
    model = Category
    template_name = "documentation/category_create_update.html"
    form_class = CategoryForm

    def test_func(self):
        return self.request.user.is_superuser

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Ajouter une catégorie documentaire"
        context["back_url"] = reverse("documentation:category_list")
        return context


class CategoryUpdateView(UserPassesTestMixin, UpdateView):
    model = Category
    template_name = "documentation/category_create_update.html"
    form_class = CategoryForm

    def test_func(self):
        return self.request.user.is_superuser

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = f"Mettre à jour la catégorie {self.object.name}"
        context["back_url"] = self.object.get_absolute_url()
        return context
