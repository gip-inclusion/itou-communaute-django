from haystack import views

from lacommunaute.forum_search.forms import SearchForm


class FacetedSearchView(views.FacetedSearchView):
    form_class = SearchForm
    template = "forum_search/search.html"
