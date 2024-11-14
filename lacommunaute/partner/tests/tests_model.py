import pytest
from django.conf import settings
from django.db import IntegrityError

from lacommunaute.partner.factories import PartnerFactory
from lacommunaute.partner.models import Partner


def test_name_uniqueness(db):
    partner = PartnerFactory()
    with pytest.raises(IntegrityError):
        PartnerFactory(name=partner.name)


def test_slug_is_generated(db):
    partner = Partner.objects.create(name="Test Partner")
    assert partner.slug == "test-partner"


def test_logo_url(db):
    partner = PartnerFactory(with_logo=True)
    assert (
        partner.logo.url.split("?")[0] == f"{settings.MEDIA_URL}{settings.AWS_STORAGE_BUCKET_NAME}/{partner.logo.name}"
    )
    assert "AWSAccessKeyId=" in partner.logo.url


def test_get_absolute_url(db):
    partner = PartnerFactory()
    assert partner.get_absolute_url() == f"/partenaires/{partner.slug}-{partner.pk}/"


def test_ordering(db):
    partners = PartnerFactory.create_batch(2)
    assert list(Partner.objects.all()) == partners[::-1]
    partners[0].save()
    assert list(Partner.objects.all()) == partners
