from datetime import datetime, timedelta

from dateutil.relativedelta import relativedelta
from django.conf import settings
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone, translation
from django.utils.formats import date_format
from faker import Faker

from lacommunaute.event.factories import EventFactory
from lacommunaute.event.forms import EventModelForm
from lacommunaute.event.models import Event
from lacommunaute.users.factories import UserFactory


faker = Faker()


class EventModelFormTest(TestCase):
    def test_required_fields(self):
        form = EventModelForm(data={})
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors["name"], ["Ce champ est obligatoire."])
        self.assertEqual(form.errors["date"], ["Ce champ est obligatoire."])
        self.assertEqual(form.errors["time"], ["Ce champ est obligatoire."])
        self.assertEqual(form.errors["end_date"], ["Ce champ est obligatoire."])
        self.assertEqual(form.errors["end_time"], ["Ce champ est obligatoire."])

    def test_dates_are_not_in_the_past(self):
        form = EventModelForm(
            data={
                "date": timezone.now().date() - relativedelta(days=2),
                "time": timezone.now().time(),
                "end_date": timezone.now().date() - relativedelta(days=1),
                "end_time": timezone.now().time(),
            }
        )
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors["date"], ["La date ne peut pas être dans le passé."])
        self.assertEqual(form.errors["end_date"], ["La date ne peut pas être dans le passé."])

    def test_end_date_is_after_date(self):
        form = EventModelForm(
            data={
                "date": timezone.now().date() + relativedelta(days=1),
                "time": timezone.now().time(),
                "end_date": timezone.now().date(),
                "end_time": timezone.now().time(),
            }
        )
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors["end_date"], ["La date de fin doit être après la date de début."])

    def test_end_time_is_after_time(self):
        end_time = datetime.now() - timedelta(hours=1)
        form = EventModelForm(
            data={
                "date": datetime.now().date(),
                "time": datetime.now().time(),
                "end_date": datetime.now().date(),
                "end_time": end_time.time(),
            }
        )
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors["end_time"], ["L'heure de fin doit être après l'heure de début."])


class EventCreateViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = UserFactory()
        cls.url = reverse("event:create")

    def test_login_is_required(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("inclusion_connect:authorize") + "?next=" + self.url)

    def test_event_is_created(self):
        self.client.force_login(self.user)
        data = {
            "name": faker.name(),
            "date": timezone.now().date(),
            "time": timezone.now().time(),
            "end_date": timezone.now().date(),
            "end_time": timezone.now().time(),
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Event.objects.count(), 1)
        self.assertEqual(Event.objects.get().poster, self.user)

    def test_event_is_not_created_with_invalid_data(self):
        self.client.force_login(self.user)
        data = {
            "name": faker.name(),
            "date": timezone.now().date(),
            "time": timezone.now().time(),
            "end_date": timezone.now().date() - relativedelta(days=1),
            "end_time": timezone.now().time(),
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Event.objects.count(), 0)


class EventUpdateViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.event = EventFactory()
        cls.user = cls.event.poster
        cls.url = reverse("event:update", kwargs={"pk": cls.event.pk})

    def test_login_is_required(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 403)

    def test_event_does_not_exist(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse("event:update", kwargs={"pk": 999}))
        self.assertEqual(response.status_code, 404)

    def test_event_is_not_mine(self):
        event = EventFactory()
        self.client.force_login(self.user)
        response = self.client.get(reverse("event:update", kwargs={"pk": event.id}))
        self.assertEqual(response.status_code, 403)

    def test_event_is_mine(self):
        self.client.force_login(self.user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)  # 200 = OK

    def test_event_is_updated(self):
        self.client.force_login(self.user)
        response = self.client.get(self.url)
        data = {
            "name": faker.name(),
            "date": timezone.now().date(),
            "time": timezone.now().time(),
            "end_date": timezone.now().date(),
            "end_time": timezone.now().time(),
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Event.objects.count(), 1)
        event = Event.objects.get()
        self.assertEqual(event.poster, self.user)
        self.assertEqual(event.name, data["name"])
        self.assertEqual(event.date, data["date"])
        self.assertEqual(event.time, data["time"])
        self.assertEqual(event.end_date, data["end_date"])
        self.assertEqual(event.end_time, data["end_time"])


class EventDeleteViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.event = EventFactory()
        cls.user = cls.event.poster
        cls.url = reverse("event:delete", kwargs={"pk": cls.event.pk})

    def test_login_is_required(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 403)

    def test_event_does_not_exist(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse("event:delete", kwargs={"pk": 999}))
        self.assertEqual(response.status_code, 404)

    def test_event_is_not_mine(self):
        event = EventFactory()
        self.client.force_login(self.user)
        response = self.client.get(reverse("event:delete", kwargs={"pk": event.id}))
        self.assertEqual(response.status_code, 403)

    def test_event_is_mine(self):
        self.client.force_login(self.user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)


class EventListViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.url = reverse("event:myevents")
        cls.user = UserFactory()

    def test_login_is_required(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("inclusion_connect:authorize") + "?next=" + self.url)

        self.client.force_login(self.user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_list_my_events(self):
        myevent = EventFactory(poster=self.user)
        not_myevent = EventFactory()
        self.client.force_login(self.user)

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertIn(myevent, response.context_data["object_list"])
        self.assertNotIn(not_myevent, response.context_data["object_list"])


class EventDetailViewTest(TestCase):
    def test_detail_view(self):
        event = EventFactory()
        response = self.client.get(reverse("event:detail", kwargs={"pk": event.pk}))
        self.assertContains(response, event.name, status_code=200)


class EventMonthArchiveViewTest(TestCase):
    def test_view_wo_args(self):
        event = EventFactory(date=timezone.now())
        response = self.client.get(reverse("event:current"))
        self.assertContains(response, event.name, status_code=200)
        self.assertContains(response, reverse("event:detail", kwargs={"pk": event.pk}))
        self.assertContains(response, reverse("event:create"))

    def test_view_with_args(self):
        event = EventFactory(date=timezone.now() + relativedelta(months=1))
        response = self.client.get(reverse("event:month", kwargs={"year": event.date.year, "month": event.date.month}))
        self.assertContains(response, event.name, status_code=200)

    def test_allow_empty(self):
        response = self.client.get(reverse("event:month", kwargs={"year": 2000, "month": 1}))
        self.assertContains(response, "Aucun évènement", status_code=200, html=True)

    def test_navbar(self):
        with translation.override(settings.LANGUAGE_CODE):
            current_date = timezone.now()
            next_month = current_date + relativedelta(months=1)
            previous_month = current_date - relativedelta(months=1)

            response = self.client.get(reverse("event:current"))
            self.assertContains(response, date_format(current_date, "F Y"), status_code=200)

        self.assertContains(
            response,
            reverse(
                "event:month",
                kwargs={
                    "year": previous_month.year,
                    "month": f"{previous_month.month:02d}",
                },
            ),
            status_code=200,
        )
        self.assertContains(
            response,
            reverse(
                "event:month",
                kwargs={
                    "year": next_month.year,
                    "month": f"{next_month.month:02d}",
                },
            ),
            status_code=200,
        )
