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
    return reverse("documentation:category_update", kwargs={"slug": category.slug, "pk": category.pk})


@pytest.fixture(name="superuser")
def fixture_superuser(db):
    return UserFactory(is_superuser=True)


@pytest.mark.parametrize(
    "user,status_code", [(None, 302), (lambda: UserFactory(), 403), (lambda: UserFactory(is_superuser=True), 200)]
)
def test_user_passes_test_mixin(client, db, url, user, status_code):
    if user:
        client.force_login(user())
    response = client.get(url)
    assert response.status_code == status_code


@pytest.fixture(name="expected_context")
def fixture_expected_context(category):
    return {
        "title": f"Modifier la catégorie {category.name}",
        "back_url": reverse("documentation:category_detail", kwargs={"slug": category.slug, "pk": category.pk}),
    }


def test_view(client, db, url, superuser, expected_context):
    client.force_login(superuser)
    response = client.get(url)
    assert response.status_code == 200
    assert {k: response.context[k] for k in expected_context.keys()} == expected_context
    assert response.context["form"].fields.keys() == {"name", "short_description", "description", "image"}


@pytest.fixture(name="post_data")
def fixture_post_data():
    return {
        "name": "New Name",
        "short_description": "New Short Description",
        "description": "### New Description",
    }


@pytest.fixture(name="expected_values")
def fixture_expected_values(post_data):
    return {
        "name": post_data["name"],
        "short_description": post_data["short_description"],
        "_description_rendered": "<h3>New Description</h3>",
        "slug": "new-name",
    }


def test_update(client, db, url, superuser, post_data, expected_values):
    client.force_login(superuser)
    response = client.post(url, post_data)
    assert response.status_code == 302
    category = Category.objects.get(slug=expected_values["slug"])
    assert {k: getattr(category, k) for k in expected_values.keys()} == expected_values
