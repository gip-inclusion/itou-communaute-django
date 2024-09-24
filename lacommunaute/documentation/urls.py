from django.urls import path

from lacommunaute.documentation.views import CategoryCreateView, CategoryDetailView, CategoryListView


app_name = "documentation"


urlpatterns = [
    path("", CategoryListView.as_view(), name="category_list"),
    path("<str:slug>-<int:pk>/", CategoryDetailView.as_view(), name="category_detail"),
    path("category/create/", CategoryCreateView.as_view(), name="category_create"),
]
