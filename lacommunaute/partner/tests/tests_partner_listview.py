import pytest  # noqa
from django.urls import reverse

from lacommunaute.partner.factories import PartnerFactory
from lacommunaute.users.factories import UserFactory
from lacommunaute.utils.testing import parse_response_to_soup


@pytest.fixture(name="url")
def url_fixture():
    return reverse("partner:list")


def test_listview(client, db, snapshot, url):
    partner = PartnerFactory(for_snapshot=True, with_image=True)
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


@pytest.mark.parametrize(
    "user,link_is_visible",
    [(None, False), (lambda: UserFactory(), False), (lambda: UserFactory(is_superuser=True), True)],
)
def test_link_to_createview(client, db, url, user, link_is_visible):
    if user:
        client.force_login(user())
    response = client.get(url)
    assert response.status_code == 200
    assert bool(reverse("partner:create") in response.content.decode()) == link_is_visible
