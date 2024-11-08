from django import forms
from django.conf import settings

from lacommunaute.partner.models import Partner


class PartnerForm(forms.ModelForm):
    logo = forms.ImageField(
        required=False,
        label="Logo, format 200 x 200 pixels recommandé",
        widget=forms.FileInput(attrs={"accept": settings.SUPPORTED_IMAGE_FILE_TYPES.keys()}),
    )

    class Meta:
        model = Partner
        fields = ("name", "short_description", "description", "logo", "url")
