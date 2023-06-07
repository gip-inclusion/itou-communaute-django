from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from machina.core.loading import get_class

from lacommunaute.forum_stats.enums import Period
from lacommunaute.forum_stats.factories import StatFactory
from lacommunaute.users.factories import UserFactory


assign_perm = get_class("forum_permission.shortcuts", "assign_perm")


class HomepageTest(TestCase):
    def test_home_page(self):
        url = reverse("forum_conversation_extension:home")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "pages/home.html")


class StatistiquesPageTest(TestCase):
    def test_context_data(self):
        url = reverse("pages:statistiques")
        date = timezone.now()
        names = ["nb_uniq_engaged_visitors", "nb_uniq_visitors", "nb_uniq_active_visitors"]
        for name in names:
            StatFactory(name=name, date=date)
        undesired_period_stat = StatFactory(
            period=Period.WEEK, date=date - timezone.timedelta(days=7), name="nb_uniq_engaged_visitors"
        )
        undesired_date_stat = StatFactory(
            period=Period.DAY, date=date - timezone.timedelta(days=91), name="nb_uniq_engaged_visitors"
        )

        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "pages/statistiques.html")

        # expected values
        self.assertIn("stats", response.context)
        self.assertIn("date", response.context["stats"])
        self.assertIn("nb_uniq_engaged_visitors", response.context["stats"])
        self.assertIn("nb_uniq_visitors", response.context["stats"])
        self.assertIn("nb_uniq_active_visitors", response.context["stats"])
        self.assertEqual(response.context["stats"]["date"][0], date.strftime("%Y-%m-%d"))

        # undesired values
        self.assertNotIn(undesired_period_stat.date.strftime("%Y-%m-%d"), response.context["stats"]["date"])
        self.assertNotIn(undesired_date_stat.date.strftime("%Y-%m-%d"), response.context["stats"]["date"])


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
        self.assertEqual(response.status_code, 403)

        self.client.force_login(UserFactory(is_superuser=True))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "pages/landing_pages.html")
