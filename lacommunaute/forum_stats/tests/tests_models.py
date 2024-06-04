from dateutil.relativedelta import relativedelta
from django.db import IntegrityError
from django.test import TestCase
from django.utils import timezone
from django.utils.timezone import localdate

from lacommunaute.forum_stats.enums import Period
from lacommunaute.forum_stats.factories import StatFactory
from lacommunaute.forum_stats.models import Stat


class StatModelTest(TestCase):
    def test_uniqueness(self):
        date = timezone.now()
        name = "nb_unique_contributors"
        period = Period.DAY
        StatFactory(name=name, date=date, period=period)
        with self.assertRaises(IntegrityError):
            StatFactory(name=name, date=date, period=period)


class StatQuerySetTest(TestCase):
    def test_ordering(self):
        today = localdate()
        stat = StatFactory(period=Period.MONTH, date=today)
        StatFactory(period=Period.DAY, date=today)
        StatFactory(period=Period.MONTH, date=today - relativedelta(months=1))

        qs = Stat.objects.current_month_datas()
        self.assertEqual(list(qs), [{"name": stat.name, "value": stat.value, "date": today}])

    def test_empty_dataset(self):
        self.assertEqual(Stat.objects.current_month_datas().count(), 0)
