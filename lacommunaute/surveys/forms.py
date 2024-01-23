from django import forms

from lacommunaute.surveys.models import DSP
from lacommunaute.surveys.recommendations import get_recommendations


class DSPForm(forms.ModelForm):
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
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        model = self._meta.model
        for fieldname, formfield in self.fields.items():
            modelfield = model._meta.get_field(fieldname)
            formfield.widget = forms.RadioSelect(choices=modelfield.choices)

    def save(self, commit=True):
        instance = super().save(commit=commit)
        recommendations = get_recommendations(instance)
        instance.recommendations.set(recommendations)
        return instance
