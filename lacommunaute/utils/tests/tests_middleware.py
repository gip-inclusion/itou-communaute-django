from django.test import TestCase, override_settings


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
