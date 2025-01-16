import pytest
from django.test import override_settings
from pytest_django.asserts import assertTemplateUsed


@pytest.mark.parametrize(
    "parking_page, expected_template",
    [
        (True, "middleware/parking.html"),
        (False, "pages/home.html"),
    ],
)
def test_parking_page_middleware(client, db, parking_page, expected_template):
    with override_settings(PARKING_PAGE=parking_page):
        response = client.get("/")
        assert response.status_code == 200
        assertTemplateUsed(response, expected_template)
