from django import forms
from django.utils.translation import gettext_lazy as _

from .enums import CommonIndexKind


class SearchForm(forms.Form):
    m = forms.ChoiceField(
        choices=(
            ("all", "tout le site"),
            (CommonIndexKind.TOPIC, "les échanges"),
            (CommonIndexKind.FORUM, "la documentation"),
        ),
        required=False,
        widget=forms.RadioSelect,
        label=_("Search in"),
    )
    q = forms.CharField(
        max_length=255,
        required=False,
        label=_("Search for keywords"),
        widget=forms.TextInput(
            attrs={
                "placeholder": _("Keywords or phrase"),
                "type": "search",
            }
        ),
    )
