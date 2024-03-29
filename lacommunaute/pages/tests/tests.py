from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from django.utils.dateformat import format
from django.utils.timezone import localdate
from faker import Faker
from machina.core.loading import get_class

from lacommunaute.forum_stats.enums import Period
from lacommunaute.forum_stats.factories import StatFactory
from lacommunaute.users.factories import UserFactory
from lacommunaute.utils.math import percent


faker = Faker()
assign_perm = get_class("forum_permission.shortcuts", "assign_perm")


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

    def test_month_datas_in_context(self):
        today = localdate()
        url = reverse("pages:statistiques")

        # no data
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["period"], None)
        self.assertEqual(response.context["nb_uniq_visitors"], 0)
        self.assertEqual(response.context["nb_uniq_active_visitors"], 0)
        self.assertEqual(response.context["nb_uniq_engaged_visitors"], 0)
        self.assertEqual(response.context["activation_percent"], 0)
        self.assertEqual(response.context["engagement_percent"], 0)

        # undesired data
        StatFactory(name="nb_uniq_engaged_visitors", period=Period.DAY, date=today)
        StatFactory(name=faker.word(), period=Period.MONTH, date=today)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["period"], None)
        self.assertEqual(response.context["nb_uniq_visitors"], 0)
        self.assertEqual(response.context["nb_uniq_active_visitors"], 0)
        self.assertEqual(response.context["nb_uniq_engaged_visitors"], 0)
        self.assertEqual(response.context["activation_percent"], 0)
        self.assertEqual(response.context["engagement_percent"], 0)

        uniq_visitors = StatFactory(name="nb_uniq_visitors", period=Period.MONTH, date=today)
        uniq_active_visitors = StatFactory(name="nb_uniq_active_visitors", period=Period.MONTH, date=today)
        uniq_engaged_visitors = StatFactory(name="nb_uniq_engaged_visitors", period=Period.MONTH, date=today)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["period"], format(today, "F Y"))
        self.assertEqual(response.context["nb_uniq_visitors"], uniq_visitors.value)
        self.assertEqual(response.context["nb_uniq_active_visitors"], uniq_active_visitors.value)
        self.assertEqual(response.context["nb_uniq_engaged_visitors"], uniq_engaged_visitors.value)
        self.assertEqual(
            response.context["activation_percent"], percent(uniq_active_visitors.value, uniq_visitors.value)
        )
        self.assertEqual(
            response.context["engagement_percent"], percent(uniq_engaged_visitors.value, uniq_active_visitors.value)
        )

    def test_impact_in_context_data(self):
        url = reverse("pages:statistiques")
        today = localdate()
        empty_res = {"date": [], "nb_uniq_visitors_returning": []}

        # no data
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["impact"], empty_res)

        # undesired data
        StatFactory(name="nb_uniq_visitors_returning", period=Period.DAY, date=today)
        StatFactory(name=faker.word(), period=Period.MONTH, date=today)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["impact"], empty_res)

        # desired data
        StatFactory(name="nb_uniq_visitors_returning", period=Period.MONTH, date=today, value=1)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["impact"]["date"][0], today.strftime("%Y-%m-%d"))
        self.assertEqual(response.context["impact"]["nb_uniq_visitors_returning"][0], 1)


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
