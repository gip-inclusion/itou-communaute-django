from haystack import views

from lacommunaute.forum.enums import Kind as ForumKind
from lacommunaute.forum.models import Forum
from lacommunaute.forum_search.forms import SearchForm


class FacetedSearchView(views.FacetedSearchView):
    form_class = SearchForm
    template = "forum_search/search.html"

    def extra_context(self):
        extra = super().extra_context()
        extra["forum"] = Forum.objects.filter(kind=ForumKind.PUBLIC_FORUM, lft=1, level=0).first()
        return extra
