import pytest
from dateutil.relativedelta import relativedelta
from django.db import IntegrityError
from django.test import TestCase
from django.utils import timezone
from django.utils.timezone import localdate

from lacommunaute.stats.enums import Period
from lacommunaute.stats.factories import ForumStatFactory, StatFactory
from lacommunaute.stats.models import ForumStat, Stat


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


class TestForumStat:
    def test_ordering(self, db):
        first_forumstat = ForumStatFactory(date=localdate())
        second_forumstat = ForumStatFactory(
            forum=first_forumstat.forum,
            date=first_forumstat.date + relativedelta(days=1),
            period=first_forumstat.period,
        )

        assert list(ForumStat.objects.all()) == [first_forumstat, second_forumstat]

    def test_uniqueness(self, db):
        forumstat = ForumStatFactory()
        forumstat.id = None
        with pytest.raises(IntegrityError):
            forumstat.save()
