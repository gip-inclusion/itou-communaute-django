from django.urls import path
from haystack.views import search_view_factory

from lacommunaute.forum_search.forms import SearchForm
from lacommunaute.forum_search.views import FacetedSearchView


app_name = "forum_search_extension"


urlpatterns = [
    path(
        "search/",
        search_view_factory(view_class=FacetedSearchView, form_class=SearchForm),
        name="search",
    ),
]
