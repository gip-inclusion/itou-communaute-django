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

        if self.get_tags():
            qs = qs.filter(tags__in=self.get_tags())

        return qs

    def get_tags(self, flat=None):
        if not hasattr(self, "tags"):
            try:
                request_tags = self.request.GET["tags"]
            except KeyError:
                self.tags = Tag.objects.none()
            else:
                self.tags = Tag.objects.filter(slug__in=request_tags.lower().split(","))

        if flat == "name":
            return " ou ".join(tag.name for tag in self.tags)
        if flat == "slug":
            return ",".join(tag.slug for tag in self.tags)
        return self.tags

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
            "active_tags": self.get_tags(flat="slug"),
            "active_tags_label": self.get_tags(flat="name"),
            "active_filter_name": getattr(Filters, active_filter, Filters.ALL).label,
            "filters": Filters.choices,
        }
