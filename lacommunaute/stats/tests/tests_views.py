from datetime import date

import pytest  # noqa
from dateutil.relativedelta import relativedelta
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from django.utils.dateformat import format
from django.utils.timezone import localdate
from faker import Faker
from freezegun import freeze_time
from machina.core.loading import get_class
from pytest_django.asserts import assertContains, assertNotContains

from lacommunaute.documentation.factories import CategoryFactory, DocumentFactory, DocumentRatingFactory
from lacommunaute.stats.enums import Period
from lacommunaute.stats.factories import ForumStatFactory, StatFactory
from lacommunaute.surveys.factories import DSPFactory
from lacommunaute.utils.math import percent
from lacommunaute.utils.testing import parse_response_to_soup


faker = Faker()
assign_perm = get_class("forum_permission.shortcuts", "assign_perm")


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
    category = CategoryFactory()
    fa = DocumentFactory(name="A", category=category)
    fb = DocumentFactory(name="B", category=category)
    fc = DocumentFactory(name="C", category=category)
    fd = DocumentFactory(name="D", category=category)
    # ForumStatFactory(forum=fa, period="week", visits=70, time_spent=40 * 60)
    # ForumStatFactory(forum=fb, period="week", visits=100, time_spent=30 * 60)
    # ForumStatFactory(forum=fc, period="week", visits=90, time_spent=20 * 60)
    # ForumStatFactory(forum=fd, period="week", visits=80, time_spent=10 * 60)
    DocumentRatingFactory.create_batch(2, document=fa, rating=4)
    DocumentRatingFactory.create_batch(1, document=fb, rating=3)
    DocumentRatingFactory.create_batch(4, document=fc, rating=2)
    DocumentRatingFactory.create_batch(3, document=fd, rating=5)

    # undesired forum
    DocumentFactory(name="Orphelin Document")
    DocumentFactory(name="Document wo DocumentStats", category=category)

    return category


class TestForumStatView:
    @pytest.mark.parametrize(
        "sort_key,snapshot_name",
        [
            (None, "sort_by_sum_time_spent"),
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
                response,
                selector="main",
                replace_in_href=[document for document in document_stats_setup.documents.all()],
            )
        ) == snapshot(name=snapshot_name)

    def test_num_queries(self, client, db, document_stats_setup, django_assert_num_queries):
        django_session_num_of_queries = 6
        expected_queries_in_view = 1
        with django_assert_num_queries(expected_queries_in_view + django_session_num_of_queries):
            client.get(reverse("stats:document_stats"))


class TestForumStatWeekArchiveView:
    def get_url_from_date(self, date):
        return reverse(
            "stats:forum_stat_week_archive", kwargs={"year": date.strftime("%Y"), "week": date.strftime("%W")}
        )

    def test_header_and_breadcrumb(self, client, db, snapshot):
        response = client.get(self.get_url_from_date(ForumStatFactory(for_snapshot=True).date))
        assert response.status_code == 200
        assert str(parse_response_to_soup(response, selector=".s-title-01")) == snapshot(name="title-01")
        assert str(parse_response_to_soup(response, selector=".c-breadcrumb")) == snapshot(name="breadcrumb")

    def test_navigation(self, client, db):
        weeks = [date.today() - relativedelta(weeks=i) for i in range(15, 10, -1)]
        for week in weeks[1:4]:
            ForumStatFactory(date=week, for_snapshot=True)

        test_cases = [
            {"test_week": weeks[1], "not_contains": [weeks[0]], "contains": [weeks[2]]},
            {"test_week": weeks[2], "not_contains": [], "contains": [weeks[1], weeks[3]]},
            {"test_week": weeks[3], "not_contains": [weeks[4]], "contains": [weeks[2]]},
        ]

        for test_case in test_cases:
            response = client.get(self.get_url_from_date(test_case["test_week"]))
            for week in test_case["not_contains"]:
                assertNotContains(response, self.get_url_from_date(week))
            for week in test_case["contains"]:
                assertContains(response, self.get_url_from_date(week))

        # out of bound
        for week in [weeks[0], weeks[4]]:
            response = client.get(self.get_url_from_date(week))
            assert response.status_code == 404

    def test_most_viewed_forums(self, client, db, snapshot):
        forums_stats = [
            ForumStatFactory(for_snapshot=True, visits=10, entry_visits=8, time_spent=1000, forum__name="Forum A"),
            ForumStatFactory(for_snapshot=True, visits=17, entry_visits=5, time_spent=1978, forum__name="Forum B"),
        ]

        response = client.get(self.get_url_from_date(forums_stats[0].date))
        assert response.status_code == 200
        assert str(
            parse_response_to_soup(
                response, selector="#most_viewed", replace_in_href=[fs.forum for fs in forums_stats]
            )
        ) == snapshot(name="most_viewed_forums")

    def test_paginated_most_viewed_forums(self, client, db):
        ForumStatFactory.create_batch(16, for_snapshot=True)
        response = client.get(reverse("stats:forum_stat_week_archive", kwargs={"year": 2024, "week": 21}))
        assert response.status_code == 200
        assert len(response.context_data["forum_stats"]) == 15

    def test_most_rated_documents(self, client, db, snapshot):
        # required to unblock the view, until ForumStat is migrated to the new model
        fs = ForumStatFactory(for_snapshot=True, forum__name="Forum A")
        document = DocumentFactory(name="Document A")

        # rating within range
        DocumentRatingFactory.create_batch(2, rating=5, document=document, set_created=fs.date)
        # rating out of range
        DocumentRatingFactory.create_batch(2, rating=1, document=document)

        # undesired document
        DocumentFactory()

        # undesired rating
        DocumentRatingFactory(rating=4)

        response = client.get(self.get_url_from_date(fs.date))
        assert response.status_code == 200
        assert str(parse_response_to_soup(response, selector="#most_rated")) == snapshot(name="most_rated_documents")

    def test_visitors(self, client, db, snapshot):
        fs = ForumStatFactory(for_snapshot=True)

        # relevant
        relevant_dates = [
            fs.date,
            fs.date + relativedelta(days=6),
            fs.date + relativedelta(days=6) - relativedelta(days=89),
        ]
        visitors = [10, 11, 12]
        for stat_date, visitor_count in zip(relevant_dates, visitors):
            StatFactory(date=stat_date, name="nb_uniq_visitors", value=visitor_count)

        # undesired
        for stat_date in [fs.date + relativedelta(weeks=1), fs.date + relativedelta(days=6) - relativedelta(days=90)]:
            StatFactory(date=stat_date, name="nb_uniq_visitors", value=99)

        response = client.get(self.get_url_from_date(fs.date))
        assert response.status_code == 200
        expected_stats = {
            "date": ["2024-02-27", "2024-05-20", "2024-05-26"],
            "nb_uniq_visitors": [12, 10, 11],
            "nb_uniq_engaged_visitors": [],
        }
        assert response.context_data["stats"] == expected_stats


@pytest.mark.parametrize(
    "forum_stats,status_code",
    [
        (lambda: None, 404),
        (lambda: [ForumStatFactory(for_snapshot=True), ForumStatFactory(for_snapshot_older=True)], 302),
    ],
)
def test_redirect_to_latest_weekly_stats(client, db, forum_stats, status_code):
    forum_stats = forum_stats()
    response = client.get(reverse("stats:redirect_to_latest_weekly_stats"))
    assert response.status_code == status_code
    if forum_stats:
        assert response.url == reverse(
            "stats:forum_stat_week_archive",
            kwargs={"year": forum_stats[0].date.year, "week": forum_stats[0].date.strftime("%W")},
        )
