import pytest  # noqa
from django.urls import reverse

from lacommunaute.documentation.factories import CategoryFactory
from lacommunaute.utils.testing import parse_response_to_soup


@pytest.fixture(name="url")
def fixture_url():
    return reverse("documentation:category_list")


@pytest.mark.parametrize(
    "objects,status_code,snapshot_name",
    [
        ([], 200, "category_list_view_is_empty"),
        (
            [(f"titre {i}", f"short desc {i}", f"desc {i}") for i in range(1, 4)],
            200,
            "category_list_view_with_categories",
        ),
    ],
)
def test_category_list_view(client, db, url, objects, status_code, snapshot_name, snapshot):
    categories = [
        CategoryFactory(name=titre, short_description=short_desc, description=desc)
        for titre, short_desc, desc in objects
    ]
    response = client.get(url)
    assert response.status_code == status_code
    content = parse_response_to_soup(response, selector="main", replace_img_src=True, replace_in_href=categories)
    assert str(content) == snapshot(name=snapshot_name)
