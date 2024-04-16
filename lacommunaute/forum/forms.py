from django import forms

from lacommunaute.forum.models import Forum


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

    class Meta:
        model = Forum
        fields = ["name", "short_description", "description"]
