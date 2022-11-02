from django.test import TestCase
from django.urls import reverse


class HomepageTest(TestCase):
    def test_home_page(self):
        url = reverse("pages:home")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "pages/home.html")
