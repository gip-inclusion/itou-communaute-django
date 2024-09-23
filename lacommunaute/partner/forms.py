from django import forms
from django.conf import settings

from lacommunaute.partner.models import Partner
from lacommunaute.utils.html import wrap_iframe_in_div_tag


class PartnerForm(forms.ModelForm):
    logo = forms.ImageField(
        required=False,
        label="Logo, format 200 x 200 pixels recommandé",
        widget=forms.FileInput(attrs={"accept": settings.SUPPORTED_IMAGE_FILE_TYPES.keys()}),
    )

    def save(self, commit=True):
        partner = super().save(commit=False)
        partner.description = wrap_iframe_in_div_tag(self.cleaned_data.get("description"))

        if commit:
            partner.save()

        return partner

    class Meta:
        model = Partner
        fields = ("name", "short_description", "description", "logo", "url")
