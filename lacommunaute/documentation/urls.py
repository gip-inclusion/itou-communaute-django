from django.urls import path

from lacommunaute.documentation.views import CategoryListView


app_name = "documentation"


urlpatterns = [
    path("", CategoryListView.as_view(), name="category_list"),
]
