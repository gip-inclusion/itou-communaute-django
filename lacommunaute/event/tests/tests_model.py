from dateutil.relativedelta import relativedelta
from django.db import IntegrityError
from django.test import TestCase
from django.utils import timezone

from lacommunaute.event.factories import EventFactory
from lacommunaute.event.models import Event


class EventCurrentUpcomingManagerTest(TestCase):
    def test_manager(self):
        now = timezone.now()

        EventFactory(date=now)

        old_event = EventFactory(date=now - relativedelta(months=1))

        # upcomming event
        EventFactory(date=now + relativedelta(months=1))

        # Event at the beginning of the current month
        EventFactory(date=now.replace(now.year, now.month, 1))

        self.assertEqual(Event.current_and_upcomings.count(), 3)
        self.assertNotIn(old_event, Event.current_and_upcomings.all())


class EventModelTest(TestCase):
    def test_user_is_mandatory(self):
        with self.assertRaises(IntegrityError):
            EventFactory(poster=None)
