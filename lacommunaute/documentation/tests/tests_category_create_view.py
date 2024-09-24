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


@pytest.mark.parametrize(
    "user,status_code", [(None, 302), (lambda: UserFactory(), 403), (lambda: UserFactory(is_superuser=True), 200)]
)
def test_user_passes_test_mixin(client, db, url, user, status_code):
    if user:
        client.force_login(user())
    response = client.get(url)
    assert response.status_code == status_code


@pytest.fixture(name="expected_context")
def fixture_expected_context():
    return {
        "title": "Créer une nouvelle catégorie",
        "back_url": reverse("documentation:category_list"),
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
        "name": "Test Name",
        "short_description": "Test Short Description",
        "description": "## Test Description\n- with markdown",
    }


@pytest.fixture(name="expected_values")
def fixture_expected_values():
    return {
        "name": "Test Name",
        "short_description": "Test Short Description",
        "_description_rendered": "<h2>Test Description</h2>\n\n<ul>\n<li>with markdown</li>\n</ul>",
        "slug": "test-name",
    }


def test_create_category(client, db, url, superuser, post_data, expected_values):
    client.force_login(superuser)
    response = client.post(url, data=post_data)
    assert response.status_code == 302

    category = Category.objects.get()
    assert {k: getattr(category, k) for k in expected_values.keys()} == expected_values
