from django.test import TestCase
from django.urls import reverse


class HomepageTest(TestCase):
    def test_home_page(self):
        url = reverse("pages:home")
        response = self.client.get(url)
        self.assertContains(response, "Bienvenue sur la communauté de l'inclusion")
