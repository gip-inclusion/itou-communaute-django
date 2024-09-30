import pytest  # noqa

from lacommunaute.documentation.factories import CategoryFactory, DocumentFactory
from lacommunaute.users.factories import UserFactory
from lacommunaute.utils.testing import parse_response_to_soup


@pytest.fixture(name="category")
def fixture_category():
    return CategoryFactory(for_snapshot=True)


@pytest.mark.parametrize(
    "active_tag, snapshot_name",
    [
        ("tag1", "category_detail_view_with_active_tag"),
        (None, "category_detail_view_without_active_tag"),
        ("unknowntag", "category_detail_view_with_unknown_tag"),
    ],
)
def test_category_detail_view_with_tagged_documents(client, db, category, active_tag, snapshot_name, snapshot):
    DocumentFactory(category=category, with_tags=["tag1", "tag2"], for_snapshot=True)
    DocumentFactory(category=category, for_snapshot=True, name="Document without tags")
    url = f"{category.get_absolute_url()}?tag={active_tag}" if active_tag else category.get_absolute_url()
    response = client.get(url)
    assert response.status_code == 200
    content = parse_response_to_soup(
        response,
        selector="main",
        replace_img_src=True,
        replace_in_href=[category] + [doc for doc in category.documents.all()],
    )
    assert str(content) == snapshot(name=snapshot_name)


@pytest.mark.parametrize(
    "user,link_is_visible",
    [(None, False), (lambda: UserFactory(), False), (lambda: UserFactory(is_superuser=True), True)],
)
def test_link_to_update_view(client, db, category, user, link_is_visible):
    if user:
        client.force_login(user())
    response = client.get(category.get_absolute_url())
    assert response.status_code == 200
    assert bool(category.get_update_url() in response.content.decode()) == link_is_visible


@pytest.mark.parametrize(
    "headers,expected_template_name",
    [(None, "documentation/category_detail.html"), ({"HX-Request": True}, "documentation/document_list.html")],
)
def test_template_name(client, db, category, headers, expected_template_name):
    response = client.get(category.get_absolute_url(), headers=headers)
    assert response.status_code == 200
    assert response.template_name == [expected_template_name]


# test numqueries with and without tag
