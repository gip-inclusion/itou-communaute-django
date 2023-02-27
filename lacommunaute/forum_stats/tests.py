from django.db import IntegrityError
from django.test import TestCase
from django.utils import timezone

from lacommunaute.forum_stats.enums import Period
from lacommunaute.forum_stats.factories import StatFactory


class StatModelTest(TestCase):
    def test_uniqueness(self):
        date = timezone.now()
        name = "nb_unique_contributors"
        period = Period.DAY
        StatFactory(name=name, date=date, period=period)
        with self.assertRaises(IntegrityError):
            StatFactory(name=name, date=date, period=period)
