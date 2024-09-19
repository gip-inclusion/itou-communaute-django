import pytest  # noqa

from django.urls import reverse

from lacommunaute.documentation.models import Category
from lacommunaute.users.factories import UserFactory


@pytest.fixture(name="url")
def fixture_url():
    return reverse("documentation:category_create")


@pytest.fixture(name="superuser")
def fixture_superuser(db):
    return UserFactory(is_superuser=True)


def test_user_pass_test_mixin(client, db, url, superuser):
    response = client.get(url)
    assert response.status_code == 302

    client.force_login(superuser)
    response = client.get(url)
    assert response.status_code == 200


def test_context(client, db, url, superuser):
    client.force_login(superuser)
    response = client.get(url)
    assert response.status_code == 200
    assert response.context["title"] == "Ajouter une catégorie documentaire"
    assert response.context["back_url"] == reverse("documentation:category_list")
    assert response.context["form"].fields.keys() == {"name", "short_description", "description", "image"}
    assert response.context["form"].fields["name"].required
    assert response.context["form"].fields["short_description"].required


def test_create_category(client, db, url, superuser):
    client.force_login(superuser)
    response = client.post(
        url,
        data={
            "name": "Test Name",
            "short_description": "Test Short Description",
            "description": "Test Description",
        },
    )
    assert response.status_code == 302

    category = Category.objects.get()
    assert category.name == "Test Name"
    assert category.short_description == "Test Short Description"
    assert category.description.raw == "Test Description"
    assert category.slug == "test-name"


# TODO tester avec image
