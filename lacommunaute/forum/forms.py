import re

from django import forms
from django.conf import settings
from django.forms import CharField, CheckboxSelectMultiple, ModelMultipleChoiceField
from taggit.models import Tag

from lacommunaute.forum.models import Forum


def wrap_iframe_in_div_tag(text):
    # iframe tags must be wrapped in a div tag to be displayed correctly
    # add div tag if not present

    iframe_regex = r"((<div>)?<iframe.*?</iframe>(</div>)?)"

    for match, starts_with, ends_with in re.findall(iframe_regex, text, re.DOTALL):
        if not starts_with and not ends_with:
            text = text.replace(match, f"<div>{match}</div>")

    return text


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
    certified = forms.BooleanField(required=False, label="Certifiée par la communauté de l'inclusion")
    tags = ModelMultipleChoiceField(
        label="Sélectionner un ou plusieurs tags",
        queryset=Tag.objects.all(),
        widget=CheckboxSelectMultiple,
        required=False,
    )
    new_tags = CharField(required=False, label="Ajouter un tag ou plusieurs tags (séparés par des virgules)")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk:
            self.fields["tags"].initial = self.instance.tags.all()

    def save(self, commit=True):
        forum = super().save(commit=False)
        forum.description = wrap_iframe_in_div_tag(self.cleaned_data.get("description"))

        if commit:
            forum.save()
            forum.tags.set(self.cleaned_data["tags"])
            (
                forum.tags.add(*[tag.strip() for tag in self.cleaned_data["new_tags"].split(",")])
                if self.cleaned_data.get("new_tags")
                else None
            )
        return forum

    class Meta:
        model = Forum
        fields = ["name", "short_description", "description", "image", "certified"]
