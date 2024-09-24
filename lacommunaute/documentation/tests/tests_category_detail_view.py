import pytest  # noqa

from lacommunaute.documentation.factories import CategoryFactory, DocumentFactory
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
    url = f"{category.get_absolute_url()}?tag={active_tag}" if active_tag else category.get_absolute_url()
    response = client.get(url)
    assert response.status_code == 200
    content = parse_response_to_soup(response, selector="main", replace_img_src=True, replace_in_href=[category])
    assert str(content) == snapshot(name=snapshot_name)
