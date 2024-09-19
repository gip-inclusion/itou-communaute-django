from django.urls import path

from lacommunaute.documentation.views import CategoryDetailView, CategoryListView, DocumentDetailView


app_name = "documentation"


urlpatterns = [
    path("", CategoryListView.as_view(), name="category_list"),
    path("<str:slug>-<int:pk>/", CategoryDetailView.as_view(), name="category_detail"),
]
