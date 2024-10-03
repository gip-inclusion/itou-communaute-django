from taggit.models import Tag

from lacommunaute.forum_conversation.enums import Filters


class FilteredTopicsListViewMixin:
    """
    Provides behaviour for filtering topics with forum filtering options
    """

    def filter_queryset(self, qs):
        filter = self.request.GET.get("filter")

        if filter == Filters.NEW:
            qs = qs.unanswered()
        elif filter == Filters.CERTIFIED:
            qs = qs.filter(certified_post__isnull=False)

        if self.get_tag():
            qs = qs.filter(tags=self.get_tag())

        return qs

    def get_tag(self):
        if not hasattr(self, "tag"):
            try:
                request_tag = self.request.GET["tag"]
            except KeyError:
                self.tag = Tag.objects.none()
            else:
                self.tag = Tag.objects.filter(slug=request_tag.lower()).first()

        return self.tag

    def get_load_more_url(self, url):
        """
        :return: a URL for pagination
        """
        if self.request.GET:
            params = self.request.GET.copy()
            params.pop("page", None)
            url += f"?{params.urlencode()}"
        return url

    def get_topic_filter_context(self):
        active_filter = self.request.GET.get("filter", Filters.ALL)

        return {
            "active_tag": self.get_tag(),
            "active_filter_name": getattr(Filters, active_filter, Filters.ALL).label,
            "filters": Filters.choices,
        }
