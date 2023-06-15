from django.utils.translation import gettext_lazy as _
from haystack.forms import FacetedSearchForm
from machina.core.loading import get_class


PermissionHandler = get_class("forum_permission.handler", "PermissionHandler")


class SearchForm(FacetedSearchForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["q"].label = _("Search for keywords")
        self.fields["q"].widget.attrs["placeholder"] = _("Keywords or phrase")
        self.fields["q"].required = True

    def search(self):
        sqs = super().search()

        if not self.is_valid():
            return self.no_query_found()

        return sqs
