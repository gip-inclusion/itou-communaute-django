from django import forms
from django.conf import settings

from lacommunaute.forum.models import Forum
from lacommunaute.utils.iframe import wrap_iframe_in_div_tag


class ForumForm(forms.ModelForm):
    name = forms.CharField(required=True, label="Titre")
    short_description = forms.CharField(
        widget=forms.Textarea(attrs={"rows": 3}),
        max_length=400,
        required=True,
        label="Sous-titre (400 caractères pour le SEO)",
    )
    description = forms.CharField(
        widget=forms.Textarea(attrs={"rows": 20}), required=False, label="Contenu (markdown autorisé)"
    )
    image = forms.ImageField(
        required=False,
        label="Banniere de couverture, format 1200 x 630 pixels recommandé",
        widget=forms.FileInput(attrs={"accept": settings.SUPPORTED_IMAGE_FILE_TYPES.keys()}),
    )

    def save(self, commit=True):
        forum = super().save(commit=False)
        forum.description = wrap_iframe_in_div_tag(self.cleaned_data.get("description"))

    class Meta:
        model = Forum
        fields = [
            "name",
            "short_description",
            "description",
            "image",
        ]
