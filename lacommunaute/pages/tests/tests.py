from django.test import TestCase
from django.urls import reverse

from lacommunaute.users.factories import UserFactory


class LandingPagesListViewTest(TestCase):
    def test_context_data(self):
        url = reverse("pages:landing_pages")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)

        self.client.force_login(UserFactory())
        response = self.client.get(url)
        self.assertEqual(response.status_code, 403)

        self.client.force_login(UserFactory(is_staff=True))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "pages/landing_pages.html")
