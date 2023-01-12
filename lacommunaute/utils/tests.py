from datetime import datetime, timedelta

from dateutil.relativedelta import relativedelta
from django.core.files.uploadedfile import SimpleUploadedFile
from django.db.models.functions import TruncMonth, TruncWeek
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
from lacommunaute.utils.stats import count_objects_per_period, format_counts_of_objects_for_timeline_chart


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
    def test_count_objects_per_period(self):
        now = timezone.now()
        one_month_ago = now - relativedelta(months=1)
        UserFactory(date_joined=one_month_ago)
        UserFactory.create_batch(2, date_joined=now)

        # test format month
        self.assertEqual(
            count_objects_per_period(User.objects.annotate(period=TruncMonth("date_joined")), "users"),
            [{"period": one_month_ago.strftime("%b %Y"), "users": 1}, {"period": now.strftime("%b %Y"), "users": 2}],
        )

        # test format week
        self.assertEqual(
            count_objects_per_period(User.objects.annotate(period=TruncWeek("date_joined")), "users", period="WEEK"),
            [{"period": one_month_ago.strftime("%Y-%W"), "users": 1}, {"period": now.strftime("%Y-%W"), "users": 2}],
        )

        # test unknown format
        with self.assertRaises(ValueError):
            count_objects_per_period(User.objects.annotate(period=TruncWeek("date_joined")), "users", period="XXX")

    def test_format_counts_of_objects_for_timeline_chart(self):
        datas = [{"period": "Dec 2022", "posts": 1}, {"period": "Feb 2023", "posts": 2}] + [
            {"period": "Dec 2022", "users": 1},
            {"period": "Jan 2023", "users": 2},
        ]
        self.assertEqual(
            format_counts_of_objects_for_timeline_chart(datas),
            {"period": ["Dec 2022", "Feb 2023", "Jan 2023"], "users": [1, 0, 2], "posts": [1, 2, 0]},
        )
