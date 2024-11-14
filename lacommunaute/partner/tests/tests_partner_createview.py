import pytest
from django.urls import reverse

from lacommunaute.partner.models import Partner
from lacommunaute.users.factories import UserFactory


@pytest.fixture(name="url")
def url_fixture():
    return reverse("partner:create")


@pytest.fixture(name="superuser")
def superuser_fixture():
    return UserFactory(is_superuser=True)


@pytest.mark.parametrize(
    "user,status_code", [(None, 302), (lambda: UserFactory(), 403), (lambda: UserFactory(is_superuser=True), 200)]
)
def test_user_passes_test_mixin(client, db, url, user, status_code):
    if user:
        client.force_login(user())
    response = client.get(url)
    assert response.status_code == status_code


def test_view(client, db, url, superuser):
    client.force_login(superuser)
    response = client.get(url)
    assert response.status_code == 200
    assert response.context["title"] == "Créer une nouvelle page partenaire"
    assert response.context["back_url"] == reverse("partner:list")
    assert list(response.context["form"].fields.keys()) == ["name", "short_description", "description", "logo", "url"]


def test_post_partner(client, db, url, superuser):
    client.force_login(superuser)
    data = {
        "name": "Test",
        "short_description": "Short description",
        "description": "# Titre\ntext",
        "url": "https://www.example.com",
    }
    response = client.post(url, data)
    assert response.status_code == 302

    partner = Partner.objects.get()
    assert response.url == reverse("partner:detail", kwargs={"pk": partner.pk, "slug": partner.slug})
    assert partner.description.raw == "# Titre\ntext"
