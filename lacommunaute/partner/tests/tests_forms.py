from lacommunaute.partner.forms import PartnerForm
from lacommunaute.partner.models import Partner


def test_form_field():
    form = PartnerForm()
    assert form.Meta.model == Partner
    assert form.Meta.fields == ("name", "short_description", "description", "logo", "url")
    assert form.fields["name"].required
    assert list(form.fields["logo"].widget.attrs["accept"]) == ["image/png", "image/jpeg", "image/jpg", "image/gif"]
