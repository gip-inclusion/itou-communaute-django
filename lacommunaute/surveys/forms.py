from django import forms
from django.conf import settings

from lacommunaute.surveys.models import DSP
from lacommunaute.surveys.recommendations import get_recommendations


class DSPForm(forms.ModelForm):
    location = forms.CharField(
        label="Localisation",
        required=True,
        widget=forms.Select(attrs={"class": "form-select", "data-ajax--url": f"{settings.API_BAN_BASE_URL}/search/"}),
    )
    city_code = forms.CharField(widget=forms.HiddenInput(), required=False)

    class Meta:
        model = DSP
        fields = [
            "work_capacity",
            "language_skills",
            "housing",
            "rights_access",
            "mobility",
            "resources",
            "judicial",
            "availability",
            "location",
            "city_code",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        model = self._meta.model
        for fieldname, formfield in self.fields.items():
            if isinstance(formfield, forms.ChoiceField):
                modelfield = model._meta.get_field(fieldname)
                formfield.widget = forms.RadioSelect(choices=modelfield.choices)

    def save(self, commit=True):
        instance = super().save(commit=commit)
        recommendations = get_recommendations(instance)
        instance.recommendations.set(recommendations)
        return instance
