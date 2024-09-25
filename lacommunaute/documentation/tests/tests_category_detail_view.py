import pytest  # noqa

from django.urls import reverse

from lacommunaute.documentation.factories import CategoryFactory, DocumentFactory
from lacommunaute.utils.testing import parse_response_to_soup
from lacommunaute.users.factories import UserFactory


@pytest.fixture(name="category")
def fixture_category():
    return CategoryFactory(for_snapshot=True)


@pytest.fixture(name="url")
def fixture_url(category):
    return reverse("documentation:category_detail", kwargs={"pk": category.pk, "slug": category.slug})


@pytest.mark.parametrize(
    "active_tag, snapshot_name",
    [
        ("tag1", "category_detail_view_with_active_tag"),
        (None, "category_detail_view_without_active_tag"),
        ("unknowntag", "category_detail_view_with_unknown_tag"),
    ],
)
def test_category_detail_view_with_tagged_documents(client, db, url, category, active_tag, snapshot_name, snapshot):
    DocumentFactory(category=category, with_tags=["tag1", "tag2"], for_snapshot=True)
    if active_tag:
        url = f"{url}?tag={active_tag}"
    response = client.get(url)
    assert response.status_code == 200
    content = parse_response_to_soup(response, selector="main", replace_img_src=True, replace_in_href=[category])
    assert str(content) == snapshot(name=snapshot_name)


@pytest.mark.parametrize(
    "user_factory,link_is_visible",
    [
        (None, False),
        (UserFactory, False),
        (lambda: UserFactory(is_superuser=True), True),
    ],
)
def test_update_link_is_visible_for_superuser_only(client, db, url, category, user_factory, link_is_visible):
    user = user_factory() if user_factory else None
    if user:
        client.force_login(user)

    response = client.get(url)
    assert response.status_code == 200

    category_update_url = reverse("documentation:category_update", kwargs={"pk": category.pk, "slug": category.slug})
    if link_is_visible:
        assert category_update_url in str(response.content)
    else:
        assert category_update_url not in str(response.content)
