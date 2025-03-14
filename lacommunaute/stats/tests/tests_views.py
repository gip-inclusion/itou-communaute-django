from datetime import date

import pytest
from dateutil.relativedelta import relativedelta
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from django.utils.dateformat import format
from django.utils.timezone import localdate
from faker import Faker
from freezegun import freeze_time
from pytest_django.asserts import assertContains

from lacommunaute.forum.factories import CategoryForumFactory, ForumFactory, ForumRatingFactory
from lacommunaute.stats.enums import Period
from lacommunaute.stats.factories import ForumStatFactory, StatFactory
from lacommunaute.surveys.factories import DSPFactory
from lacommunaute.utils.math import percent
from lacommunaute.utils.testing import parse_response_to_soup


faker = Faker()


class StatistiquesPageTest(TestCase):
    def test_context_data(self):
        url = reverse("stats:statistiques")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "stats/statistiques.html")

    def test_month_datas_in_context(self):
        today = localdate()
        url = reverse("stats:statistiques")

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
        url = reverse("stats:statistiques")
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
        url = reverse("stats:statistiques")
        response = self.client.get(url)
        self.assertContains(response, f"<a href={reverse('stats:monthly_visitors')}>")


@pytest.fixture(name="setup_statistiques_data")
def setup_statistiques_data_fixture(request):
    last_visible_date = date(2024, 6, 30)
    first_visible_date = last_visible_date - timezone.timedelta(days=89)
    if request.param == "undesired_data_setup":
        return [
            StatFactory(name="nb_uniq_visitors", date=first_visible_date, period=Period.MONTH),
            StatFactory(name="nb_uniq_visitors", date=first_visible_date, period=Period.WEEK),
            StatFactory(name=faker.word(), date=first_visible_date, period=Period.DAY),
            StatFactory(
                name="nb_uniq_visitors", date=first_visible_date - timezone.timedelta(days=1), period=Period.DAY
            ),
            StatFactory(
                name="nb_uniq_visitors", date=last_visible_date + timezone.timedelta(days=1), period=Period.DAY
            ),
        ]
    if request.param == "desired_data_setup":
        stats = [
            ("nb_uniq_visitors", first_visible_date, 8469),
            ("nb_uniq_visitors", last_visible_date, 8506),
            ("nb_uniq_engaged_visitors", first_visible_date, 128),
            ("nb_uniq_engaged_visitors", last_visible_date, 5040),
        ]
        return [StatFactory(name=name, date=date, value=value) for name, date, value in stats]
    return None


class TestStatistiquesPageView:
    def test_dsp_count(self, client, db, snapshot):
        DSPFactory.create_batch(10)
        url = reverse("stats:statistiques")
        response = client.get(url)
        assert response.status_code == 200
        assert str(parse_response_to_soup(response, selector="#daily_dsp")) == snapshot(name="dsp")

    @pytest.mark.parametrize(
        "setup_statistiques_data,expected",
        [
            (
                None,
                {"date": [], "nb_uniq_visitors": [], "nb_uniq_engaged_visitors": []},
            ),
            (
                "undesired_data_setup",
                {"date": [], "nb_uniq_visitors": [], "nb_uniq_engaged_visitors": []},
            ),
            (
                "desired_data_setup",
                {
                    "date": ["2024-04-02", "2024-06-30"],
                    "nb_uniq_visitors": [8469, 8506],
                    "nb_uniq_engaged_visitors": [128, 5040],
                },
            ),
        ],
        indirect=["setup_statistiques_data"],
    )
    def test_visitors_in_context_data(self, client, db, setup_statistiques_data, expected):
        with freeze_time("2024-07-01"):
            url = reverse("stats:statistiques")
            response = client.get(url)
        assert response.status_code == 200
        assert response.context["stats"] == expected

    def test_link_to_document_stats_view(self, client, db):
        url = reverse("stats:statistiques")
        response = client.get(url)
        assert response.status_code == 200
        assertContains(response, reverse("stats:document_stats"))


class TestMonthlyVisitorsView:
    def test_context_data(self, client, db):
        url = reverse("stats:monthly_visitors")
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
        assert response.context["box_title"] == "Utilisateurs uniques mensuels"
        assert response.context["stats"] == empty_res

        # undesired data
        StatFactory(name="nb_uniq_visitors_returning", period=Period.DAY, date=today)
        StatFactory(name=faker.word(), period=Period.MONTH, date=today)
        StatFactory(name="nb_uniq_visitors", period=Period.MONTH, date=today - relativedelta(months=9), value=1)
        response = client.get(url)
        assert response.status_code == 200
        assert response.context["stats"] == empty_res

        # expected data
        StatFactory(name="nb_uniq_visitors_returning", period=Period.MONTH, date=today, value=2)
        StatFactory(name="nb_uniq_visitors", period=Period.MONTH, date=today - relativedelta(months=8), value=10)
        response = client.get(url)
        assert response.status_code == 200
        assert response.context["stats"] == {
            "date": [(today - relativedelta(months=8)).strftime("%Y-%m-%d"), today.strftime("%Y-%m-%d")],
            "nb_uniq_visitors": [10],
            "nb_uniq_active_visitors": [],
            "nb_uniq_engaged_visitors": [],
            "nb_uniq_visitors_returning": [2],
        }

    def test_navigation(self, client, db, snapshot):
        url = reverse("stats:dsp")
        response = client.get(url)
        assert response.status_code == 200
        assert str(parse_response_to_soup(response, selector=".c-breadcrumb")) == snapshot(name="breadcrumb")


class TestDailyDSPView:
    def test_context_data(self, client, db):
        today = localdate()

        # undesired datas
        StatFactory(name="dsp", period=Period.DAY, date=today - relativedelta(months=3), value=20)
        StatFactory(name=faker.word(), period=Period.DAY, date=today, value=21)

        # expected datas
        StatFactory(
            name="dsp", period=Period.DAY, date=today - relativedelta(months=3) + relativedelta(days=1), value=3
        )
        StatFactory(name="dsp", period=Period.DAY, date=today, value=2)

        url = reverse("stats:dsp")
        response = client.get(url)
        assert response.status_code == 200
        assert response.context["box_title"] == "Diagnostics Parcours IAE quotidiens"
        assert response.context["stats"] == {
            "date": [
                (today - relativedelta(months=3) + relativedelta(days=1)).strftime("%Y-%m-%d"),
                today.strftime("%Y-%m-%d"),
            ],
            "dsp": [3, 2],
        }

    def test_navigation(self, client, db, snapshot):
        url = reverse("stats:dsp")
        response = client.get(url)
        assert response.status_code == 200
        assert str(parse_response_to_soup(response, selector=".c-breadcrumb")) == snapshot(name="breadcrumb")


@pytest.fixture(name="document_stats_setup")
def document_stats_setup_fixture(db):
    category_A = CategoryForumFactory(name="category A")
    category_B = CategoryForumFactory(name="category B")
    fa = ForumFactory(name="A", parent=category_A)
    fb = ForumFactory(name="B", parent=category_A)
    fc = ForumFactory(name="C", parent=category_B)
    fd = ForumFactory(name="D", parent=category_B)
    ForumStatFactory(forum=fa, period="week", visits=70, time_spent=40 * 60)
    ForumStatFactory(forum=fb, period="week", visits=100, time_spent=30 * 60)
    ForumStatFactory(forum=fc, period="week", visits=90, time_spent=20 * 60)
    ForumStatFactory(forum=fd, period="week", visits=80, time_spent=10 * 60)
    ForumRatingFactory.create_batch(2, forum=fa, rating=4)
    ForumRatingFactory.create_batch(1, forum=fb, rating=3)
    ForumRatingFactory.create_batch(4, forum=fc, rating=2)
    ForumRatingFactory.create_batch(3, forum=fd, rating=5)

    # undesired forum
    ForumFactory(name="Forum not in Document area")
    ForumFactory(name="Forum wo ForumStats", parent=category_A)

    return list(category_A.get_children()) + list(category_B.get_children())


class TestForumStatView:
    @pytest.mark.parametrize(
        "sort_key,snapshot_name",
        [
            (None, "sort_by_sum_time_spent"),
            ("parent", "sort_by_parent"),
            ("sum_time_spent", "sort_by_sum_time_spent"),
            ("sum_visits", "sort_by_sum_visits"),
            ("avg_rating", "sort_by_avg_rating"),
            ("count_rating", "sort_by_count_rating"),
            ("unknown", "sort_by_sum_time_spent"),
        ],
    )
    def test_sort_key(self, client, db, document_stats_setup, sort_key, snapshot_name, snapshot):
        url = reverse("stats:document_stats") + f"?sort={sort_key}" if sort_key else reverse("stats:document_stats")
        response = client.get(url)
        assert response.status_code == 200
        assert str(
            parse_response_to_soup(
                response, selector="main", replace_in_href=[forum for forum in document_stats_setup]
            )
        ) == snapshot(name=snapshot_name)

    def test_num_queries(self, client, db, document_stats_setup, django_assert_num_queries):
        django_session_num_of_queries = 6
        expected_queries_in_view = 1
        with django_assert_num_queries(expected_queries_in_view + django_session_num_of_queries):
            client.get(reverse("stats:document_stats"))
