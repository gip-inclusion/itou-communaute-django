import pytest  # noqa
from django.urls import reverse

from lacommunaute.partner.factories import PartnerFactory
from lacommunaute.utils.testing import parse_response_to_soup


@pytest.fixture(name="url")
def url_fixture():
    return reverse("partner:list")


def test_listview(client, db, snapshot, url):
    partner = PartnerFactory(for_snapshot=True, with_logo=True)
    response = client.get(url)
    assert response.status_code == 200
    assert str(
        parse_response_to_soup(response, selector="#partner-list", replace_img_src=True, replace_in_href=[partner])
    ) == snapshot(name="partner_listview")


def test_pagination(client, db, snapshot, url):
    PartnerFactory.create_batch(8 * 3 + 1)
    response = client.get(url)
    assert response.status_code == 200
    assert str(parse_response_to_soup(response, selector="ul.pagination")) == snapshot(name="partner_pagination")
