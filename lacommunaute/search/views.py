from logging import getLogger

from django.contrib.postgres.search import SearchHeadline, SearchQuery, SearchRank
from django.db.models import F
from django.views.generic import ListView
from django.views.generic.edit import FormMixin

from lacommunaute.forum.models import Forum
from lacommunaute.search.enums import CommonIndexKind
from lacommunaute.search.forms import SearchForm
from lacommunaute.search.models import CommonIndex


logger = getLogger("lacommunaute")


class SearchView(FormMixin, ListView):
    model = CommonIndex
    form_class = SearchForm
    paginate_by = 10

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        data = self.request.GET.copy()
        data.setdefault("m", "all")
        kwargs["data"] = data
        return kwargs

    def get_queryset(self):
        queryset = super().get_queryset()
        form = self.get_form()
        if not form.is_valid() or not form.cleaned_data["q"]:
            return queryset.none()
        search_query = SearchQuery(
            form.cleaned_data["q"],
            config="french",
            search_type="websearch",
        )
        search_kind = form.cleaned_data["m"]
        if search_kind in CommonIndexKind.values:
            queryset = queryset.filter(kind=search_kind)
        return (
            queryset.annotate(rank=SearchRank(F("content_ts"), search_query, cover_density=True))
            # Arbitrary threshold. From running a couple searches, good results
            # are above 1.0, standard results are above 0.2 and OK results are
            # around 0.1. Take a generous margin, and exclude irrelevant
            # results.
            .filter(rank__gte=0.01)
            .annotate(
                headline=SearchHeadline(
                    # Don’t highlight matches in title, it already stands out.
                    "content",
                    search_query,
                    config="french",
                    fragment_delimiter="…",
                    start_sel='<span class="highlighted">',
                    stop_sel="</span>",
                )
            )
            .order_by("-rank")
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["forum"] = Forum.objects.get_main_forum()
        return context
