from django.urls import path

from lacommunaute.documentation.views import (
    CategoryCreateView,
    CategoryDetailView,
    CategoryListView,
    CategoryUpdateView,
    DocumentDetailView,
)


app_name = "documentation"


urlpatterns = [
    path("", CategoryListView.as_view(), name="category_list"),
    path("<str:slug>-<int:pk>/", CategoryDetailView.as_view(), name="category_detail"),
    path("category/create/", CategoryCreateView.as_view(), name="category_create"),
    path("<str:slug>-<int:pk>/update/", CategoryUpdateView.as_view(), name="category_update"),
    path("<int:category_pk>/<str:slug>-<int:pk>/", DocumentDetailView.as_view(), name="document_detail"),
]
