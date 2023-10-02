from django.db import IntegrityError
from django.test import TestCase

from lacommunaute.event.factories import EventFactory


class EventModelTest(TestCase):
    def test_user_is_mandatory(self):
        with self.assertRaises(IntegrityError):
            EventFactory(poster=None)
