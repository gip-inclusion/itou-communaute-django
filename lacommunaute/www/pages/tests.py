from django.test import TestCase
from django.urls import reverse
from machina.core.loading import get_class


assign_perm = get_class("forum_permission.shortcuts", "assign_perm")


class HomepageTest(TestCase):
    def test_home_page(self):
        url = reverse("forum_extension:home")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "pages/home.html")


class StatistiquesPageTest(TestCase):
    def test_context_data(self):
        url = reverse("pages:statistiques")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "pages/statistiques.html")
