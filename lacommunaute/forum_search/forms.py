from django.forms import ChoiceField, RadioSelect
from django.utils.translation import gettext_lazy as _
from haystack.forms import FacetedSearchForm
from machina.core.loading import get_class

from lacommunaute.forum.models import Forum
from lacommunaute.forum_conversation.models import Post


PermissionHandler = get_class("forum_permission.handler", "PermissionHandler")


class SearchForm(FacetedSearchForm):
    MODEL_CHOICES = (
        ("all", "tout le site"),
        ("post", "les échanges"),
        ("forum", "la documentation"),
    )
    m = ChoiceField(choices=MODEL_CHOICES, required=False, widget=RadioSelect)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["m"].label = _("Search in")
        self.fields["m"].initial = kwargs.pop("initial", {}).get("m", "all")

        self.fields["q"].label = _("Search for keywords")
        self.fields["q"].widget.attrs["placeholder"] = _("Keywords or phrase")
        self.fields["q"].required = True

    def search(self):
        sqs = super().search()

        if not self.is_valid():
            return self.no_query_found()

        if self.cleaned_data.get("m") == "post":
            sqs = sqs.models(Post)
        elif self.cleaned_data.get("m") == "forum":
            sqs = sqs.models(Forum)

        return sqs
