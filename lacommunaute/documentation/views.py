from django.views.generic import ListView

from lacommunaute.documentation.models import Category


class CategoryListView(ListView):
    model = Category
    template_name = "documentation/category_list.html"
    context_object_name = "categories"
    paginate_by = 20 * 3
