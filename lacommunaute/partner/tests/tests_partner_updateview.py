import pytest
from django.urls import reverse

from lacommunaute.partner.factories import PartnerFactory
from lacommunaute.users.factories import UserFactory


@pytest.fixture(name="partner")
def partner_fixture():
    return PartnerFactory(for_snapshot=True)


@pytest.fixture(name="url")
def url_fixture(partner):
    return reverse("partner:update", kwargs={"pk": partner.id, "slug": partner.slug})


@pytest.fixture(name="saff_user")
def saff_user():
    return UserFactory(is_in_staff_group=True)


@pytest.mark.parametrize(
    "user,status_code", [(None, 302), (lambda: UserFactory(), 403), (lambda: UserFactory(is_in_staff_group=True), 200)]
)
def test_user_passes_test_mixin(client, db, url, user, status_code):
    if user:
        client.force_login(user())
    response = client.get(url)
    assert response.status_code == status_code


def test_view(client, db, url, saff_user, partner):
    client.force_login(saff_user)
    response = client.get(url)
    assert response.status_code == 200
    assert response.context["title"] == f"Modifier la page {partner.name}"
    assert response.context["back_url"] == reverse("partner:detail", kwargs={"pk": partner.pk, "slug": partner.slug})
    assert list(response.context["form"].fields.keys()) == ["name", "short_description", "description", "logo", "url"]


def test_post_partner(client, db, url, saff_user, partner):
    client.force_login(saff_user)
    data = {
        "name": "Test",
        "short_description": "Short description",
        "description": "# Titre\ndescription",
        "url": "https://www.example.com",
    }
    response = client.post(url, data)
    assert response.status_code == 302

    partner.refresh_from_db()
    assert response.url == reverse("partner:detail", kwargs={"pk": partner.pk, "slug": partner.slug})
    assert partner.description.rendered == "<h1>Titre</h1>\n\n<p>description</p>"
