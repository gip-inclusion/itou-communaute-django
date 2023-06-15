from haystack import views


class FacetedSearchView(views.FacetedSearchView):
    template = "forum_search/search.html"
