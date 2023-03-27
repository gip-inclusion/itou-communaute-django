from datetime import datetime, timedelta
from unittest.mock import patch

from dateutil.relativedelta import relativedelta
from django.core.files.uploadedfile import SimpleUploadedFile
from django.db.models.functions import TruncMonth
from django.template import Context, Template
from django.template.defaultfilters import date, time
from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils import timezone
from django.utils.encoding import force_bytes
from django.utils.http import urlencode
from django.utils.timesince import timesince
from faker import Faker

from lacommunaute.forum_conversation.factories import TopicFactory
from lacommunaute.forum_conversation.forum_attachments.factories import AttachmentFactory
from lacommunaute.users.factories import UserFactory
from lacommunaute.users.models import User
from lacommunaute.utils.enums import PeriodAggregation
from lacommunaute.utils.matomo import get_matomo_data, get_matomo_events_data, get_matomo_visits_data
from lacommunaute.utils.stats import (
    count_objects_per_period,
    format_counts_of_objects_for_timeline_chart,
    get_strftime,
)


faker = Faker()


class AttachmentsTemplateTagTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        topic = TopicFactory(with_post=True)
        cls.post = topic.posts.first()

    @override_settings(DEFAULT_FILE_STORAGE="django.core.files.storage.FileSystemStorage")
    def test_is_an_image(self):
        for filename in ["test.png", "test.jpg", "test.JPG", "test.jpeg", "test.JPEG"]:
            with self.subTest(filename=filename):
                f = SimpleUploadedFile(filename, force_bytes("file_content"))
                attachment = AttachmentFactory(post=self.post, file=f)

                out = Template("{% load attachments_tags %}" "{{ attachment|is_image }}").render(
                    Context(
                        {
                            "attachment": attachment,
                        }
                    )
                )
                self.assertEqual(out, "True")

    @override_settings(DEFAULT_FILE_STORAGE="django.core.files.storage.FileSystemStorage")
    def test_is_not_an_image(self):
        for filename in ["test.csv", "test.xlsx", "test.pdf", "test.html"]:
            with self.subTest(filename=filename):
                f = SimpleUploadedFile(filename, force_bytes("file_content"))
                attachment = AttachmentFactory(post=self.post, file=f)

                out = Template("{% load attachments_tags %}" "{{ attachment|is_image }}").render(
                    Context(
                        {
                            "attachment": attachment,
                        }
                    )
                )
                self.assertEqual(out, "False")


class SettingsContextProcessorsTest(TestCase):
    @override_settings(ALLOWED_HOSTS=["allowed.com"])
    def test_disallowed_host(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 400)
        self.assertFalse(hasattr(response.wsgi_request, "htmx"))

    def test_allowed_host(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertTrue(hasattr(response.wsgi_request, "htmx"))

    def test_htmx_request(self):
        headers = {"HX-Request": True}
        response = self.client.get("/", headers=headers)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(hasattr(response.wsgi_request, "htmx"))


class UtilsTemplateTagsTestCase(TestCase):
    def test_pluralizefr(self):
        """Test `pluralizefr` template tag."""
        template = Template("{% load str_filters %}Résultat{{ counter|pluralizefr }}")
        out = template.render(Context({"counter": 0}))
        self.assertEqual(out, "Résultat")
        out = template.render(Context({"counter": 1}))
        self.assertEqual(out, "Résultat")
        out = template.render(Context({"counter": 10}))
        self.assertEqual(out, "Résultats")

    def test_inclusion_connect_url(self):
        next_url = faker.uri()
        anchor = faker.random_int()
        inclusion_connect_url = reverse("inclusion_connect:authorize")
        context = Context({"next_url": next_url, "anchor": anchor})

        out = Template("{% load str_filters %}{% inclusion_connect_url next_url%}").render(context)
        params = {"next_url": next_url}
        self.assertEqual(out, f"{inclusion_connect_url}?{urlencode(params)}")

        out = Template("{% load str_filters %}{% inclusion_connect_url next_url anchor %}").render(context)
        params = {"next_url": f"{next_url}#{anchor}"}
        self.assertEqual(out, f"{inclusion_connect_url}?{urlencode(params)}")

    def test_relativetimesince_fr(self):
        template = Template("{% load date_filters %}{{ date|relativetimesince_fr }}")

        d = datetime.now() - timedelta(hours=1)
        out = template.render(Context({"date": d}))
        self.assertEqual(out, f"il y a {timesince(d)}")

        d = datetime.now() - timedelta(days=2)
        out = template.render(Context({"date": d}))
        self.assertEqual(out, f"{date(d,'l')}, {time(d)}")

        d = datetime.now() - timedelta(days=10)
        out = template.render(Context({"date": d}))
        self.assertEqual(out, f"le {date(d)}, {time(d)}")

    def test_urlizetrunc_target_blank(self):
        template = Template("{% load str_filters %}{{ url|urlizetrunc_target_blank:16 }}")
        out = template.render(Context({"url": "www.neuralia.co/mission"}))
        self.assertEqual(
            out, '<a target="_blank" href="http://www.neuralia.co/mission" rel="nofollow">www.neuralia.co…</a>'
        )


class UtilsStatsTest(TestCase):
    def test_get_strftime(self):
        self.assertEqual(get_strftime(PeriodAggregation.WEEK), "%Y-%W")
        self.assertEqual(get_strftime(PeriodAggregation.MONTH), "%b %Y")
        with self.assertRaises(ValueError):
            get_strftime("xxx")

    def test_count_objects_per_period(self):
        now = timezone.localtime()
        one_month_ago = now - relativedelta(months=1)
        UserFactory(date_joined=one_month_ago)
        UserFactory.create_batch(2, date_joined=now)

        self.assertEqual(
            count_objects_per_period(User.objects.annotate(period=TruncMonth("date_joined")), "users"),
            [
                {"period": one_month_ago.replace(day=1, hour=0, minute=0, second=0, microsecond=0), "users": 1},
                {"period": now.replace(day=1, hour=0, minute=0, second=0, microsecond=0), "users": 2},
            ],
        )

    def test_format_counts_of_objects_for_timeline_chart(self):
        now = timezone.localtime()
        one_month_ago = now - relativedelta(months=1)
        two_month_ago = now - relativedelta(months=2)
        datas = [{"period": one_month_ago, "posts": 1}, {"period": now, "posts": 2}] + [
            {"period": two_month_ago, "users": 1},
            {"period": now, "users": 2},
        ]
        self.assertEqual(
            format_counts_of_objects_for_timeline_chart(datas),
            {
                "period": [two_month_ago.strftime("%b %Y"), one_month_ago.strftime("%b %Y"), now.strftime("%b %Y")],
                "users": [1, 0, 2],
                "posts": [0, 1, 2],
            },
        )
        self.assertEqual(
            format_counts_of_objects_for_timeline_chart(datas, period=PeriodAggregation.WEEK),
            {
                "period": [two_month_ago.strftime("%Y-%W"), one_month_ago.strftime("%Y-%W"), now.strftime("%Y-%W")],
                "users": [1, 0, 2],
                "posts": [0, 1, 2],
            },
        )


class UtilsGetMatomoDataTest(TestCase):
    def test_get_matomo_data(self):
        nb_uniq_visitors = faker.random_int()
        with patch("lacommunaute.utils.matomo.httpx.get") as mock_get:
            mock_get.return_value.json.return_value = {"nb_uniq_visitors": nb_uniq_visitors}
            mock_get.return_value.status_code = 200

            data = get_matomo_data("day", datetime.now(), "method")
        self.assertEqual(data, {"nb_uniq_visitors": nb_uniq_visitors})

    def test_get_matomo_data_invalid_response(self):
        with patch("lacommunaute.utils.matomo.httpx.get") as mock_get:
            mock_get.return_value.status_code = 400
            with self.assertRaises(Exception):
                get_matomo_data("day", datetime.now(), "method")

    def test_get_matomo_data_not_dict_response(self):
        with patch("lacommunaute.utils.matomo.httpx.get") as mock_get:
            mock_get.return_value.json.return_value = "not a dict"
            with self.assertRaises(Exception):
                get_matomo_data("day", datetime.now(), "method")


class UtilsGetMatomoVisitsDataTest(TestCase):
    def test_get_matomo_visits_data(self):
        nb_uniq_visitors = faker.random_int()
        today = datetime.now().date()
        expected_res = [
            {
                "period": "day",
                "date": today.strftime("%Y-%m-%d"),
                "name": "nb_uniq_visitors",
                "value": nb_uniq_visitors,
            }
        ]
        with patch("lacommunaute.utils.matomo.get_matomo_data") as mock_get_matomo_data:
            mock_get_matomo_data.return_value = {"nb_uniq_visitors": nb_uniq_visitors}
            self.assertEqual(get_matomo_visits_data(period="day", search_date=today), expected_res)

    def test_get_matomo_visits_data_without_nb_uniq_visitors(self):
        today = datetime.now().date()
        expected_res = [
            {
                "period": "day",
                "date": today.strftime("%Y-%m-%d"),
                "name": "nb_uniq_visitors",
                "value": 0,
            }
        ]
        with patch("lacommunaute.utils.matomo.get_matomo_data") as mock_get_matomo_data:
            mock_get_matomo_data.return_value = {}
            self.assertEqual(get_matomo_visits_data(period="day", search_date=today), expected_res)


class UtilsGetMatomoEventsDataTest(TestCase):
    def setUp(self):
        self.today = datetime.now().date()
        self.nb_uniq_visitors = faker.random_int()
        self.empty_res = [
            {
                "period": "day",
                "date": self.today.strftime("%Y-%m-%d"),
                "name": "nb_uniq_active_visitors",
                "value": 0,
            },
            {
                "period": "day",
                "date": self.today.strftime("%Y-%m-%d"),
                "name": "nb_uniq_engaged_visitors",
                "value": 0,
            },
        ]
        self.uniq_active_visitors_res = [
            {
                "period": "day",
                "date": self.today.strftime("%Y-%m-%d"),
                "name": "nb_uniq_active_visitors",
                "value": self.nb_uniq_visitors,
            },
            {
                "period": "day",
                "date": self.today.strftime("%Y-%m-%d"),
                "name": "nb_uniq_engaged_visitors",
                "value": 0,
            },
        ]

    def test_get_matomo_events_data_with_empty_datas(self):
        with patch("lacommunaute.utils.matomo.get_matomo_data") as mock_get_matomo_data:
            mock_get_matomo_data.return_value = []
            self.assertEqual(
                get_matomo_events_data(period="day", search_date=self.today),
                self.empty_res,
            )

    def test_get_matomo_events_data_without_nb_uniq_visitors(self):
        with patch("lacommunaute.utils.matomo.get_matomo_data") as mock_get_matomo_data:
            mock_get_matomo_data.return_value = [{}]
            self.assertEqual(
                get_matomo_events_data(period="day", search_date=self.today),
                self.empty_res,
            )

    def test_get_matomo_events_data_without_subtable(self):
        with patch("lacommunaute.utils.matomo.get_matomo_data") as mock_get_matomo_data:
            mock_get_matomo_data.return_value = [{"nb_uniq_visitors": self.nb_uniq_visitors}]
            self.assertEqual(
                get_matomo_events_data(period="day", search_date=self.today),
                self.uniq_active_visitors_res,
            )

    def test_get_matomo_events_data_with_empty_subtable(self):
        with patch("lacommunaute.utils.matomo.get_matomo_data") as mock_get_matomo_data:
            mock_get_matomo_data.return_value = [{"nb_uniq_visitors": self.nb_uniq_visitors, "subtable": []}]
            self.assertEqual(
                get_matomo_events_data(period="day", search_date=self.today),
                self.uniq_active_visitors_res,
            )

    def test_get_matomo_events_data_with_missing_nb_uniq_visitors_in_subtable(self):
        expected_res = self.uniq_active_visitors_res
        expected_res[1]["value"] = self.nb_uniq_visitors
        with patch("lacommunaute.utils.matomo.get_matomo_data") as mock_get_matomo_data:
            mock_get_matomo_data.return_value = [
                {
                    "nb_uniq_visitors": self.nb_uniq_visitors,
                    "subtable": [{"label": "view"}],
                }
            ]
            self.assertEqual(
                get_matomo_events_data(period="day", search_date=self.today),
                expected_res,
            )

    def test_get_matomo_events_data_with_all_expected_datas(self):

        nb_active_visitors = faker.random_int()
        expected_res = self.uniq_active_visitors_res
        expected_res[1]["value"] = self.nb_uniq_visitors - nb_active_visitors

        with patch("lacommunaute.utils.matomo.get_matomo_data") as mock_get_matomo_data:
            mock_get_matomo_data.return_value = [
                {
                    "nb_uniq_visitors": self.nb_uniq_visitors,
                    "subtable": [
                        {
                            "label": "view",
                            "nb_uniq_visitors": nb_active_visitors,
                        },
                    ],
                }
            ]
            self.assertEqual(
                get_matomo_events_data(period="day", search_date=self.today),
                expected_res,
            )
