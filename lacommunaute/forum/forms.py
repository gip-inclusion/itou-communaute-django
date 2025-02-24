from django import forms
from django.conf import settings
from django.forms import CharField, CheckboxSelectMultiple, ModelMultipleChoiceField
from taggit.models import Tag

from lacommunaute.forum.models import Forum
from lacommunaute.partner.models import Partner


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
    partner = forms.ModelChoiceField(
        label="Sélectionner un partenaire",
        queryset=Partner.objects.all(),
        required=False,
    )
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
        fields = ["name", "short_description", "description", "image", "certified", "partner"]


class SubCategoryForumUpdateForm(ForumForm):
    parent = forms.ModelChoiceField(
        label="Mettre à jour le parent",
        queryset=Forum.objects.filter(type=Forum.FORUM_CAT, level=0),
        required=False,
    )

    class Meta:
        model = Forum
        fields = ["name", "short_description", "description", "image", "certified", "partner", "parent"]
