from django.db import IntegrityError
from django.test import TestCase

from lacommunaute.event.factories import EventFactory
from lacommunaute.users.models import EmailLastSeen


class EventModelTest(TestCase):
    def test_user_is_mandatory(self):
        with self.assertRaises(IntegrityError):
            EventFactory(poster=None)


class TestEventModel:
    def test_email_last_seen_updated_on_save(self, db):
        EventFactory()

        email_last_seen = EmailLastSeen.objects.get()
        assert email_last_seen.last_seen_kind == "EVENT"
