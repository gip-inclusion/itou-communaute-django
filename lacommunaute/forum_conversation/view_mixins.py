from urllib.parse import urlencode

from taggit.models import Tag

from lacommunaute.forum_conversation.enums import Filters


class FilteredTopicsListViewMixin:
    """
    Provides behaviour for filtering topics with forum filtering options
    """

    def get_filter(self):
        if not hasattr(self, "filter"):
            self.filter = self.request.GET.get("filter", None)
        return self.filter

    def filter_queryset(self, qs):
        if self.get_filter() == Filters.NEW:
            qs = qs.unanswered()
        elif self.get_filter() == Filters.CERTIFIED:
            qs = qs.filter(certified_post__isnull=False)

        if self.get_tags():
            qs = qs.filter(tags__in=self.get_tags())

        return qs

    def get_tags(self, flat=None):
        if not hasattr(self, "tags"):
            self.tags = Tag.objects.filter(slug__in=self.request.GET.get("tags", "").lower().split(","))

        if flat == "name":
            return " ou ".join(self.tags.values_list("name", flat=True))
        if flat == "slug":
            return ",".join(self.tags.values_list("slug", flat=True))
        return self.tags

    def get_url_encoded_params(self):
        return urlencode(
            {k: v for k, v in {"filter": self.get_filter(), "tags": self.get_tags(flat="slug")}.items() if v}
        )

    def get_load_more_url(self, url):
        """
        :return: a URL for pagination
        """
        encoded_params = self.get_url_encoded_params()
        if encoded_params:
            url += f"?{encoded_params}"
        return url

    def get_topic_filter_context(self, topic_count):
        return {
            "active_tags": self.get_tags(flat="slug"),
            "active_tags_label": self.get_tags(flat="name"),
            "active_filter_name": (
                getattr(Filters, self.get_filter(), Filters.ALL).label if self.get_filter() else Filters.ALL.label
            ),
            "filters": Filters.choices,
            "total": topic_count,
        }
