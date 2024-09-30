import pytest  # noqa

from lacommunaute.partner.forms import PartnerForm
from lacommunaute.partner.models import Partner


def test_saved_partner_description(db):
    form = PartnerForm(
        data={
            "name": "test",
            "short_description": "test",
            "description": "Text\n<iframe src='xxx'></iframe>\ntext\n<div><iframe src='yyy'></iframe></div>\nbye",
        }
    )
    assert form.is_valid()
    partner = form.save()
    assert partner.description.rendered == (
        "<p>Text</p>\n\n<div><iframe src='xxx'></iframe></div>\n\n"
        "<p>text</p>\n\n<div><iframe src='yyy'></iframe></div>\n\n<p>bye</p>"
    )


def test_form_field():
    form = PartnerForm()
    assert form.Meta.model == Partner
    assert form.Meta.fields == ("name", "short_description", "description", "logo", "url")
    assert form.fields["name"].required
    assert list(form.fields["logo"].widget.attrs["accept"]) == ["image/png", "image/jpeg", "image/jpg", "image/gif"]
