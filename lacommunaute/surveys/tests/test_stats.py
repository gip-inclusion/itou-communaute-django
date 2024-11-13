from datetime import date, datetime

from dateutil.relativedelta import relativedelta

from lacommunaute.stats.models import Stat
from lacommunaute.surveys.factories import DSPFactory
from lacommunaute.surveys.stats import collect_dsp_stats


def test_collect_dsp_stats(db):
    # no stat collected
    assert collect_dsp_stats() == (date(2024, 1, 1), 0)

    # one stat to collected for one dsp
    DSPFactory(months_ago=3)
    assert collect_dsp_stats() == (date(2024, 1, 1), 1)
    stat = Stat.objects.get()
    assert stat.name == "dsp"
    assert stat.period == "day"
    assert stat.value == 1
    assert stat.date == datetime.now().date() - relativedelta(months=3)

    # two stats to collected for two dsp, one by month
    DSPFactory(months_ago=2)
    DSPFactory(months_ago=1)
    assert collect_dsp_stats() == (stat.date + relativedelta(days=1), 2)
    assert Stat.objects.count() == 3

    # one stat to collected for three dsp in the same month
    DSPFactory.create_batch(3)
    assert collect_dsp_stats() == (datetime.now().date() - relativedelta(months=1) + relativedelta(days=1), 1)
    assert Stat.objects.count() == 4

    # no new stat to collect
    assert collect_dsp_stats() == (datetime.now().date() + relativedelta(days=1), 0)
    assert Stat.objects.count() == 4
