from django import forms

from lacommunaute.surveys.enums import (
    DSPAvailability,
    DSPHousing,
    DSPJudicial,
    DSPLanguageSkills,
    DSPMobility,
    DSPResources,
    DSPRightsAccess,
    DSPWorkCapacity,
)

from .models import DSP


class DSPForm(forms.ModelForm):
    work_capacity = forms.ChoiceField(
        widget=forms.RadioSelect,
        choices=DSPWorkCapacity.choices,
        label="Capacité à occuper un poste de travail",
        initial=None,
        required=True,
    )
    language_skills = forms.ChoiceField(
        widget=forms.RadioSelect,
        choices=DSPLanguageSkills.choices,
        label="Maîtrise de la langue française",
        initial=None,
        required=True,
    )
    housing = forms.ChoiceField(
        widget=forms.RadioSelect,
        choices=DSPHousing.choices,
        label="Logement",
        initial=None,
        required=True,
    )
    rights_access = forms.ChoiceField(
        widget=forms.RadioSelect,
        choices=DSPRightsAccess.choices,
        label="Accès aux droits",
        initial=None,
        required=True,
    )
    mobility = forms.ChoiceField(
        widget=forms.RadioSelect,
        choices=DSPMobility.choices,
        label="Mobilité",
        initial=None,
        required=True,
    )
    resources = forms.ChoiceField(
        widget=forms.RadioSelect,
        choices=DSPResources.choices,
        label="Ressources",
        initial=None,
        required=True,
    )
    judicial = forms.ChoiceField(
        widget=forms.RadioSelect,
        choices=DSPJudicial.choices,
        label="Situation judiciaire",
        initial=None,
        required=True,
    )
    availability = forms.ChoiceField(
        widget=forms.RadioSelect,
        choices=DSPAvailability.choices,
        label="Disponibilité",
        initial=None,
        required=True,
    )

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
