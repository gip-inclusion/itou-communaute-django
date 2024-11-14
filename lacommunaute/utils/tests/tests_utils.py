from datetime import date as datetime_date, datetime, timedelta
from unittest.mock import patch

import pytest
from bs4 import BeautifulSoup
from django.core.files.storage import default_storage
from django.core.files.uploadedfile import SimpleUploadedFile
from django.http import HttpResponse
from django.template import Context, Template
from django.template.defaultfilters import date, time
from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils.encoding import force_bytes
from django.utils.http import urlencode
from django.utils.timesince import timesince
from faker import Faker
from machina.core.db.models import get_model
from machina.core.loading import get_class

from lacommunaute.forum.factories import CategoryForumFactory, ForumFactory
from lacommunaute.forum_conversation.factories import TopicFactory
from lacommunaute.forum_conversation.forum_attachments.factories import AttachmentFactory
from lacommunaute.forum_file.models import PublicFile
from lacommunaute.stats.models import ForumStat
from lacommunaute.users.factories import UserFactory
from lacommunaute.utils.date import get_last_sunday
from lacommunaute.utils.html import wrap_iframe_in_div_tag
from lacommunaute.utils.math import percent
from lacommunaute.utils.matomo import (
    collect_forum_stats_from_matomo_api,
    get_matomo_data,
    get_matomo_events_data,
    get_matomo_forums_data,
    get_matomo_visits_data,
)
from lacommunaute.utils.perms import add_public_perms_on_forum
from lacommunaute.utils.testing import parse_response_to_soup
from lacommunaute.utils.urls import urlize


ForumPermission = get_model("forum_permission", "ForumPermission")
UserForumPermission = get_model("forum_permission", "UserForumPermission")

faker = Faker()

PermissionHandler = get_class("forum_permission.handler", "PermissionHandler")
assign_perm = get_class("forum_permission.shortcuts", "assign_perm")

override_storage = {"default": {"BACKEND": "django.core.files.storage.FileSystemStorage"}}


class AttachmentsTemplateTagTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        topic = TopicFactory(with_post=True)
        cls.post = topic.posts.first()

    @override_settings(STORAGES=override_storage)
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

    @override_settings(STORAGES=override_storage)
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

    @override_settings(STORAGES=override_storage)
    def test_is_available(self):
        f = SimpleUploadedFile("test.png", force_bytes("file_content"))
        attachment = AttachmentFactory(post=self.post, file=f)

        out = Template("{% load attachments_tags %}" "{{ attachment|is_available }}").render(
            Context(
                {
                    "attachment": attachment,
                }
            )
        )
        self.assertEqual(out, "True")

    @override_settings(STORAGES=override_storage)
    def test_is_not_available(self):
        f = SimpleUploadedFile("test.png", force_bytes("file_content"))
        attachment = AttachmentFactory(post=self.post, file=f)

        with patch.object(default_storage, "size", side_effect=FileNotFoundError):
            out = Template("{% load attachments_tags %}" "{{ attachment|is_available }}").render(
                Context(
                    {
                        "attachment": attachment,
                    }
                )
            )
            self.assertEqual(out.strip(), "False")


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


class UtilsUrlsTestCase(TestCase):
    def test_urlize(self):
        url = f"{faker.url()}/long_string_to_truncate/"
        self.assertEqual(urlize(url, trim_url_limit=10), f'<a href="{url}">{url[:9]}…</a>')

        link = f'<a href="{faker.url()}">{faker.name()}</a>'
        self.assertEqual(urlize(link), link)

        img = f'<img src="{faker.url()}">'
        self.assertEqual(urlize(img), img)


class TestUtilsTemplateTags:
    @pytest.mark.parametrize(
        "value,expected_result", [(900, "0h 15min"), (3600, "1h 00min"), (7320, "2h 02min"), (None, "0h 00min")]
    )
    def test_convert_seconds_into_hours(self, value, expected_result):
        template = Template("{% load date_filters %}{{ value|convert_seconds_into_hours }}")
        assert template.render(Context({"value": value})) == expected_result


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

    def test_openid_connect_url(self):
        next_url = faker.uri()
        anchor = faker.random_int()
        openid_connect_url = reverse("openid_connect:authorize")
        context = Context({"next_url": next_url, "anchor": anchor})

        out = Template("{% load str_filters %}{% openid_connect_url next_url%}").render(context)
        params = {"next": next_url}
        self.assertEqual(out, f"{openid_connect_url}?{urlencode(params)}")

        out = Template("{% load str_filters %}{% openid_connect_url next_url anchor %}").render(context)
        params = {"next": f"{next_url}#{anchor}"}
        self.assertEqual(out, f"{openid_connect_url}?{urlencode(params)}")

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
        template = Template("{% load str_filters %}{{ str|urlizetrunc_target_blank:16 }}")
        out = template.render(Context({"str": "www.neuralia.co/mission"}))
        self.assertEqual(
            out, '<a target="_blank" href="http://www.neuralia.co/mission" rel="nofollow">www.neuralia.co…</a>'
        )

        out = template.render(Context({"str": 'src="www.neuralia.co/image.png"'}))
        self.assertEqual(out, "src=&quot;www.neuralia.co/image.png&quot;")

    def test_img_fluid(self):
        template = Template("{% load str_filters %}{{ html|img_fluid }}")
        out = template.render(Context({"html": '<img src="image.png">'}))
        self.assertEqual(out, '<img class="img-fluid" src="image.png">')

    def test_url_add_query(self):
        base_url = faker.url()
        # Full URL.
        context = {"url": f"{base_url}/?status=new&page=4&page=1"}
        template = Template("{% load url_add_query %}{% url_add_query url page=2 %}")
        out = template.render(Context(context))
        expected = f"{base_url}/?status=new&amp;page=2"
        assert out == expected

        # Relative URL.
        context = {"url": "/?status=new&page=1"}
        template = Template("{% load url_add_query %}{% url_add_query url page=22 %}")
        out = template.render(Context(context))
        expected = "/?status=new&amp;page=22"
        assert out == expected

        # Empty URL.
        context = {"url": ""}
        template = Template("{% load url_add_query %}{% url_add_query url page=1 %}")
        out = template.render(Context(context))
        expected = "?page=1"
        assert out == expected


class UtilsGetMatomoDataTest(TestCase):
    @override_settings(MATOMO_BASE_URL="https://matomo.example.com")
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
        nb_uniq_visitors_returning = faker.random_int()
        today = datetime.now().date()
        expected_res = [
            {
                "period": "day",
                "date": today.strftime("%Y-%m-%d"),
                "name": "nb_uniq_visitors",
                "value": nb_uniq_visitors,
            },
            {
                "period": "day",
                "date": today.strftime("%Y-%m-%d"),
                "name": "nb_uniq_visitors_returning",
                "value": nb_uniq_visitors_returning,
            },
        ]
        with patch("lacommunaute.utils.matomo.get_matomo_data") as mock_get_matomo_data:
            mock_get_matomo_data.return_value = {
                "nb_uniq_visitors": nb_uniq_visitors,
                "nb_uniq_visitors_returning": nb_uniq_visitors_returning,
            }
            self.assertEqual(get_matomo_visits_data(period="day", search_date=today), expected_res)

    def test_get_matomo_visits_data_without_nb_uniq_visitors(self):
        today = datetime.now().date()
        expected_res = [
            {
                "period": "day",
                "date": today.strftime("%Y-%m-%d"),
                "name": "nb_uniq_visitors",
                "value": 0,
            },
            {
                "period": "day",
                "date": today.strftime("%Y-%m-%d"),
                "name": "nb_uniq_visitors_returning",
                "value": 0,
            },
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

    def test_get_matomo_events_data_with_label(self):
        label = faker.word()
        nb_active_visitors = faker.random_int()
        expected_res = self.uniq_active_visitors_res
        expected_res[1]["value"] = self.nb_uniq_visitors - nb_active_visitors

        with patch("lacommunaute.utils.matomo.get_matomo_data") as mock_get_matomo_data:
            mock_get_matomo_data.return_value = [
                {
                    "label": label,
                    "nb_uniq_visitors": self.nb_uniq_visitors,
                    "subtable": [
                        {
                            "label": "view",
                            "nb_uniq_visitors": nb_active_visitors,
                        },
                    ],
                },
                {
                    "label": "not_" + label,
                    "nb_uniq_visitors": self.nb_uniq_visitors + 1,
                    "subtable": [
                        {
                            "label": "view",
                            "nb_uniq_visitors": nb_active_visitors + 1,
                        },
                    ],
                },
            ]
            self.assertEqual(
                get_matomo_events_data(period="day", search_date=self.today, label=label),
                expected_res,
            )


@pytest.fixture(name="get_matomo_forums_data_response")
def fixture_get_matomo_forums_data_response():
    return [
        {
            "label": "forum",
            "subtable": [
                {"label": "forum-1", "nb_visits": 10, "entry_nb_visits": 100, "sum_time_spent": 1000},
                {"label": "forum-2", "nb_visits": 20, "entry_nb_visits": 200, "sum_time_spent": 2000},
                {"label": "foruX-2", "nb_visits": 21, "entry_nb_visits": 201, "sum_time_spent": 2001},
                {"label": "forum-4", "nb_visits": 14, "entry_nb_visits": 104, "sum_time_spent": 1004},
            ],
        },
        {
            "label": "home",
            "subtable": [
                {"label": "forum-3", "nb_visits": 30, "entry_nb_visits": 300, "sum_time_spent": 3000},
            ],
        },
    ]


class TestGetMatomoForumsData:
    def test_label_is_none(self):
        with pytest.raises(ValueError) as value_error:
            get_matomo_forums_data("week", datetime_date(2024, 5, 6), None)

        assert str(value_error.value) == "label must be provided"

    def test_no_ids(self, get_matomo_forums_data_response):
        with patch("lacommunaute.utils.matomo.get_matomo_data") as mock_get_matomo_data:
            mock_get_matomo_data.return_value = get_matomo_forums_data_response
            assert get_matomo_forums_data("week", datetime_date(2024, 5, 6), "forum") == []

    def test_with_ids(self, get_matomo_forums_data_response):
        with patch("lacommunaute.utils.matomo.get_matomo_data") as mock_get_matomo_data:
            mock_get_matomo_data.return_value = get_matomo_forums_data_response
            assert get_matomo_forums_data("week", datetime_date(2024, 5, 6), "forum", ids=[1, 4]) == [
                {
                    "forum_id": 1,
                    "date": "2024-05-06",
                    "period": "week",
                    "visits": 10,
                    "entry_visits": 100,
                    "time_spent": 1000,
                },
                {
                    "forum_id": 4,
                    "date": "2024-05-06",
                    "period": "week",
                    "visits": 14,
                    "entry_visits": 104,
                    "time_spent": 1004,
                },
            ]

    def test_deduplication(self, get_matomo_forums_data_response):
        with patch("lacommunaute.utils.matomo.get_matomo_data") as mock_get_matomo_data:
            mock_get_matomo_data.return_value = get_matomo_forums_data_response
            assert get_matomo_forums_data("week", datetime_date(2024, 5, 6), "forum", ids=[2]) == [
                {
                    "forum_id": 2,
                    "date": "2024-05-06",
                    "period": "week",
                    "visits": 41,
                    "entry_visits": 401,
                    "time_spent": 4001,
                },
            ]


class TestCollectForumStatsFromMatomoApi:
    def test_unsupported_period(self):
        with pytest.raises(ValueError) as value_error:
            collect_forum_stats_from_matomo_api("unsupported", datetime_date(2024, 5, 6), datetime_date(2024, 5, 13))

        assert str(value_error.value) == "Only 'week' period is supported for forum stats collection."

    def test_collect_forum_stats_from_matomo_api(self, db):
        forum_1 = ForumFactory()
        forum_2 = ForumFactory()
        catergory_forum = CategoryForumFactory(with_child=True)
        child_category_forum = catergory_forum.children.first()

        nb_visits_faker_1 = faker.random_int()
        entry_nb_visits_faker_1 = faker.random_int()
        sum_time_spent_faker_1 = faker.random_int()
        nb_visits_faker_2 = faker.random_int()
        entry_nb_visits_faker_2 = faker.random_int()
        sum_time_spent_faker_2 = faker.random_int()

        matomo_response = [
            {
                "label": "forum",
                "subtable": [
                    {"label": f"forum-{forum_2.pk}", "nb_visits": 3, "entry_nb_visits": 4, "sum_time_spent": 200},
                    {
                        "label": f"forum-{catergory_forum.pk}",
                        "nb_visits": nb_visits_faker_1,
                        "entry_nb_visits": entry_nb_visits_faker_1,
                        "sum_time_spent": sum_time_spent_faker_1,
                    },
                    {
                        "label": f"forum-{child_category_forum.pk}",
                        "nb_visits": nb_visits_faker_2,
                        "entry_nb_visits": entry_nb_visits_faker_2,
                        "sum_time_spent": sum_time_spent_faker_2,
                    },
                ],
            },
        ]

        with patch("lacommunaute.utils.matomo.get_matomo_data") as mock_get_matomo_data:
            mock_get_matomo_data.return_value = matomo_response
            collect_forum_stats_from_matomo_api(
                period="week", from_date=datetime_date(2024, 5, 6), to_date=datetime_date(2024, 5, 13)
            )

        assert ForumStat.objects.count() == 4
        assert ForumStat.objects.filter(forum__in=[forum_1, forum_2]).count() == 0
        category_forum_20240506 = ForumStat.objects.get(
            forum=catergory_forum, date=datetime(2024, 5, 6), period="week"
        )
        assert category_forum_20240506.visits == nb_visits_faker_1
        assert category_forum_20240506.entry_visits == entry_nb_visits_faker_1
        assert category_forum_20240506.time_spent == sum_time_spent_faker_1
        child_category_forum_20240506 = ForumStat.objects.get(
            forum=child_category_forum, date=datetime(2024, 5, 6), period="week"
        )
        assert child_category_forum_20240506.visits == nb_visits_faker_2
        assert child_category_forum_20240506.entry_visits == entry_nb_visits_faker_2
        assert child_category_forum_20240506.time_spent == sum_time_spent_faker_2
        assert (
            ForumStat.objects.filter(
                forum__in=[catergory_forum, child_category_forum], date=datetime(2024, 5, 13), period="week"
            ).count()
            == 2
        )


class UtilsMathPercent(TestCase):
    def test_percent(self):
        self.assertEqual(percent(2, 1), 200)
        self.assertEqual(percent(1, 2), 50)
        self.assertEqual(percent(-1, 2), -50)
        self.assertEqual(percent(1, -2), -50)
        self.assertEqual(percent(-1, -2), 50)
        self.assertEqual(percent(1, 9), 11.11)
        self.assertEqual(percent(0, 1), 0)
        self.assertEqual(percent(1, 0), 0)
        self.assertEqual(percent(0, 0), 0)


class UtilsParseResponseToSoupTest(TestCase):
    def test_parse_wo_selector(self):
        html = '<html><head></head><body><div id="foo">bar</div></body></html>'
        response = HttpResponse(html)
        assert parse_response_to_soup(response) == BeautifulSoup(html, "html.parser")

    def test_parse_with_selector(self):
        response = HttpResponse('<html><head></head><body><div id="foo">bar</div></body></html>')
        assert str(parse_response_to_soup(response, selector="#foo")) == '<div id="foo">bar</div>'

    def test_replace_in_href_mixing_tuple_and_object(self):
        topic = TopicFactory()
        response = HttpResponse(
            "<html><head></head><body>"
            f'<div><a href="http://server.com/{topic.pk}/">salmon</a></div>'
            '<div><a href="http://server.com/bream/">bream</a></div>'
            '<div><a href="http://server.com/red_mullet/">red mullet</a></div>'
            "</body></html>"
        )
        soup = parse_response_to_soup(response, replace_in_href=[topic, ("red_mullet", "slug2")])
        assert str(soup) == (
            "<html><head></head><body>"
            '<div><a href="http://server.com/[PK of Topic]/">salmon</a></div>'
            '<div><a href="http://server.com/bream/">bream</a></div>'
            '<div><a href="http://server.com/slug2/">red mullet</a></div>'
            "</body></html>"
        )

    def test_replace_in_hxpost(self):
        topic = TopicFactory()
        response = HttpResponse(
            "<html><head></head><body>"
            f'<div hx-post="/{topic.pk}/">salmon</div>'
            '<div hx-post="/bream/">bream</div>'
            '<div hx-post="/red_mullet/">red mullet</div>'
            "</body></html>"
        )
        soup = parse_response_to_soup(response, replace_in_href=[topic, ("red_mullet", "slug2")])
        assert str(soup) == (
            "<html><head></head><body>"
            '<div hx-post="/[PK of Topic]/">salmon</div>'
            '<div hx-post="/bream/">bream</div>'
            '<div hx-post="/slug2/">red mullet</div>'
            "</body></html>"
        )

    def test_replace_in_hxget(self):
        topic = TopicFactory()
        response = HttpResponse(
            "<html><head></head><body>"
            f'<div hx-get="/{topic.pk}/">salmon</div>'
            '<div hx-get="/bream/">bream</div>'
            '<div hx-get="/red_mullet/">red mullet</div>'
            "</body></html>"
        )
        soup = parse_response_to_soup(response, replace_in_href=[topic, ("red_mullet", "slug2")])
        assert str(soup) == (
            "<html><head></head><body>"
            '<div hx-get="/[PK of Topic]/">salmon</div>'
            '<div hx-get="/bream/">bream</div>'
            '<div hx-get="/slug2/">red mullet</div>'
            "</body></html>"
        )


class TestAddPublicPermsOnForum:
    def test_public_perms(self, db):
        forum = ForumFactory()
        add_public_perms_on_forum(forum)

        perms = [
            "can_see_forum",
            "can_read_forum",
            "can_start_new_topics",
            "can_reply_to_topics",
            "can_edit_own_posts",
            "can_delete_own_posts",
            "can_post_without_approval",
        ]

        assert (
            UserForumPermission.objects.filter(
                forum=forum,
                anonymous_user=True,
                authenticated_user=False,
                has_perm=True,
                permission__in=ForumPermission.objects.filter(codename__in=perms),
            ).count()
            == 7
        )
        assert (
            UserForumPermission.objects.filter(
                forum=forum,
                anonymous_user=False,
                authenticated_user=True,
                has_perm=True,
                permission__in=ForumPermission.objects.filter(codename__in=perms),
            ).count()
            == 7
        )


class TestImageSizeValidator:
    def test_size_validator(self, db):
        file = PublicFile.objects.create(
            file="test.jpg",
            user=UserFactory(),
            keywords="test",
        )
        with pytest.raises(Exception):
            file.file.size = 1024 * 1024 * 5 + 1
            file.save()


class TestTheLastSunday:
    @pytest.mark.parametrize(
        "day, expected_sunday",
        [(i, datetime(2024, 5, 12)) for i in range(12, 19)] + [(i, datetime(2024, 5, 19)) for i in range(19, 26)],
    )
    def test_the_last_sunday(self, day, expected_sunday):
        assert get_last_sunday(datetime(2024, 5, day)) == expected_sunday


class TestWrapIframeInDiv:
    @pytest.mark.parametrize(
        "input,output",
        [
            ("<iframe src='xxx'></iframe>", "<div><iframe src='xxx'></iframe></div>"),
            (
                "markdown text <iframe src='xxx'></iframe> markdown text",
                "markdown text <div><iframe src='xxx'></iframe></div> markdown text",
            ),
            ("<div><iframe src='xxx'></iframe></div>", "<div><iframe src='xxx'></iframe></div>"),
            ("<div><iframe src='xxx'></iframe> text", "<div><iframe src='xxx'></iframe></div> text"),
            ("<iframe src='xxx'></iframe></div>", "<div><iframe src='xxx'></iframe></div>"),
            (
                "<iframe src='xxx'></iframe><iframe src='yyy'></iframe>",
                "<div><iframe src='xxx'></iframe></div><div><iframe src='yyy'></iframe></div>",
            ),
            (
                "<div><iframe src='xxx'></iframe><iframe src='yyy'></iframe></div>",
                "<div><iframe src='xxx'></iframe></div><div><iframe src='yyy'></iframe></div>",
            ),
        ],
    )
    def test_wrap_iframe_in_div_tag(self, input, output):
        assert wrap_iframe_in_div_tag(input) == output
