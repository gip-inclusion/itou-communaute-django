from django import forms
from django.conf import settings
from taggit.models import Tag

from lacommunaute.documentation.models import Category, Document
from lacommunaute.partner.models import Partner
from lacommunaute.utils.iframe import wrap_iframe_in_div_tag


class DocumentationFormMixin:
    name = forms.CharField(required=True, label="Titre")
    short_description = forms.CharField(
        widget=forms.Textarea(attrs={"rows": 3}),
        max_length=400,
        required=True,
        label="Sous-titre (400 caractères pour le SEO)",
    )
    description = forms.CharField(
        widget=forms.Textarea(attrs={"rows": 20}), required=True, label="Contenu (markdown autorisé)"
    )
    image = forms.ImageField(
        label="Banniere de couverture, format 1200 x 630 pixels recommandé",
        widget=forms.FileInput(attrs={"accept": settings.SUPPORTED_IMAGE_FILE_TYPES.keys()}),
    )

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.description = wrap_iframe_in_div_tag(self.cleaned_data.get("description"))

        if commit:
            instance.save()
        return instance


class CategoryForm(forms.ModelForm, DocumentationFormMixin):
    class Meta:
        model = Category
        fields = ["name", "short_description", "description", "image"]


class DocumentForm(forms.ModelForm, DocumentationFormMixin):
    certified = forms.BooleanField(required=False, label="Certifiée par la communauté de l'inclusion")
    partner = forms.ModelChoiceField(
        label="Sélectionner un partenaire",
        queryset=Partner.objects.all(),
        required=False,
    )
    category = forms.ModelChoiceField(
        label="Sélectionner une catégorie documentaire",
        queryset=Category.objects.all(),
        required=False,
    )
    tags = forms.ModelMultipleChoiceField(
        label="Sélectionner un ou plusieurs tags",
        queryset=Tag.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False,
    )
    new_tags = forms.CharField(required=False, label="Ajouter un tag ou plusieurs tags (séparés par des virgules)")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk:
            self.fields["tags"].initial = self.instance.tags.all()

    def save(self, commit=True):
        instance = super().save(commit=False)

        if commit:
            instance.save()
            instance.tags.set(self.cleaned_data["tags"])
            (
                instance.tags.add(*[tag.strip() for tag in self.cleaned_data["new_tags"].split(",")])
                if self.cleaned_data.get("new_tags")
                else None
            )
        return instance

    class Meta:
        model = Document
        fields = ["name", "short_description", "description", "image", "certified", "partner", "category"]
