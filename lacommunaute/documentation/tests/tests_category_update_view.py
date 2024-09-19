import pytest  # noqa

from django.urls import reverse

from lacommunaute.documentation.factories import CategoryFactory
from lacommunaute.documentation.models import Category
from lacommunaute.users.factories import UserFactory


@pytest.fixture(name="category")
def fixture_category(db):
    return CategoryFactory(for_snapshot=True)


@pytest.fixture(name="url")
def fixture_url(category):
    return reverse("documentation:category_update", kwargs={"pk": category.pk, "slug": category.slug})


@pytest.fixture(name="superuser")
def fixture_superuser(db):
    return UserFactory(is_superuser=True)


def test_user_pass_test_mixin(client, db, url, superuser):
    response = client.get(url)
    assert response.status_code == 302

    client.force_login(superuser)
    response = client.get(url)
    assert response.status_code == 200


def test_context(client, db, url, superuser, category):
    client.force_login(superuser)
    response = client.get(url)
    assert response.status_code == 200
    assert response.context["title"] == "Mettre à jour la catégorie Test Category"
    assert response.context["back_url"] == category.get_absolute_url()
    assert response.context["form"].fields.keys() == {"name", "short_description", "description", "image"}
    assert response.context["form"].fields["name"].required
    assert response.context["form"].fields["short_description"].required


def test_update_category(client, db, url, superuser, category):
    client.force_login(superuser)
    response = client.post(
        url,
        data={
            "name": "Updated Name",
            "short_description": "Updated Short Description",
            "description": "Updated Description",
        },
    )
    assert response.status_code == 302

    category = Category.objects.get()
    assert category.name == "Updated Name"
    assert category.short_description == "Updated Short Description"
    assert category.description.raw == "Updated Description"
    assert category.slug == "updated-name"


# TODO tester la mise à jour de l'image
