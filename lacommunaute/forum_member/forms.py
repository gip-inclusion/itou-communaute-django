from django import forms
from machina.apps.forum_member.forms import ForumProfileForm as BaseForumProfileForm

from lacommunaute.forum_member.enums import ActiveSearch, Regions
from lacommunaute.forum_member.models import ForumProfile


class ForumProfileForm(BaseForumProfileForm):
    cv = forms.FileField(label="Curriculum Vitae", required=False)
    linkedin = forms.URLField(label="Lien vers votre profil LinkedIn", required=False)
    search = forms.ChoiceField(label="Je suis en recherche active", choices=ActiveSearch.choices, required=False)
    region = forms.ChoiceField(label="Région", choices=Regions.choices, required=False)
    internship_duration = forms.IntegerField(label="Durée du stage (en mois)", required=False)

    class Meta:
        model = ForumProfile
        fields = ["avatar", "signature", "linkedin", "cv", "search", "region", "internship_duration"]
