from dateutil.relativedelta import relativedelta
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from django.utils.dateformat import format
from django.utils.timezone import localdate
from faker import Faker
from machina.core.loading import get_class
from pytest_django.asserts import assertContains

from lacommunaute.forum_stats.enums import Period
from lacommunaute.forum_stats.factories import StatFactory
from lacommunaute.utils.math import percent


faker = Faker()
assign_perm = get_class("forum_permission.shortcuts", "assign_perm")


class StatistiquesPageTest(TestCase):
    def test_context_data(self):
        url = reverse("forum_stats:statistiques")
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
        self.assertTemplateUsed(response, "forum_stats/statistiques.html")

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
        url = reverse("forum_stats:statistiques")

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
        url = reverse("forum_stats:statistiques")
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

    def test_navigation(self):
        url = reverse("forum_stats:statistiques")
        response = self.client.get(url)
        self.assertContains(response, "<a href=/statistiques/monthly_visitors/>")


class TestMonthlyVisitorsView:
    def test_context_data(self, client, db):
        url = reverse("forum_stats:monthly_visitors")
        today = localdate()
        empty_res = {
            "date": [],
            "nb_uniq_visitors": [],
            "nb_uniq_active_visitors": [],
            "nb_uniq_engaged_visitors": [],
            "nb_uniq_visitors_returning": [],
        }

        # no data
        response = client.get(url)
        assert response.status_code == 200
        assertContains(response, "Utilisateurs uniques mensuels")
        assert response.context["monthly_visitors"] == empty_res

        # undesired data
        StatFactory(name="nb_uniq_visitors_returning", period=Period.DAY, date=today)
        StatFactory(name=faker.word(), period=Period.MONTH, date=today)
        StatFactory(name="nb_uniq_visitors", period=Period.MONTH, date=today - relativedelta(months=9), value=1)
        response = client.get(url)
        assert response.status_code == 200
        assert response.context["monthly_visitors"] == empty_res

        # expected data
        StatFactory(name="nb_uniq_visitors_returning", period=Period.MONTH, date=today, value=2)
        StatFactory(name="nb_uniq_visitors", period=Period.MONTH, date=today - relativedelta(months=8), value=10)
        response = client.get(url)
        assert response.status_code == 200
        assert response.context["monthly_visitors"] == {
            "date": [(today - relativedelta(months=8)).strftime("%Y-%m-%d"), today.strftime("%Y-%m-%d")],
            "nb_uniq_visitors": [10],
            "nb_uniq_active_visitors": [],
            "nb_uniq_engaged_visitors": [],
            "nb_uniq_visitors_returning": [2],
        }

    def test_navigation(self, client, db):
        url = reverse("forum_stats:monthly_visitors")
        response = client.get(url)
        assert response.status_code == 200
        assertContains(response, '<a href="/statistiques/">retour vers la page statistiques</a>')
