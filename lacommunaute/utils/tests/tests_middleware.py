import pytest
from django.test import TestCase, override_settings

from lacommunaute.utils.enums import Environment


class ParkingMiddlewareTest(TestCase):
    @override_settings(PARKING_PAGE=True)
    def test_parking_page_middleware(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "middleware/parking.html")

    @override_settings(PARKING_PAGE=False)
    def test_no_parking_page_middleware(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "pages/home.html")


class TestEnvironmentSettingsMiddleware:
    @pytest.mark.parametrize(
        "env,expected",
        [
            (Environment.PROD, False),
            (Environment.TEST, False),
            (Environment.DEV, True),
        ],
    )
    def test_prod_environment(self, client, db, env, expected):
        with override_settings(ENVIRONMENT=env):
            response = client.get("/")
        assert ('id="debug-mode-banner"' in response.content.decode()) == expected
