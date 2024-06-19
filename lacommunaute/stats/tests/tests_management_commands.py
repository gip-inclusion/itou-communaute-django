import pytest  # noqa
from lacommunaute.stats.management.commands.collect_matomo_stats import get_initial_from_date
from django.core.management import call_command
from lacommunaute.surveys.factories import DSPFactory
from lacommunaute.stats.factories import StatFactory


def test_collect_django_stats(db, capsys):
    DSPFactory()
    StatFactory(for_dsp_snapshot=True)
    call_command("collect_django_stats")
    captured = capsys.readouterr()
    assert captured.out.strip() == "Collecting DSP stats from 2024-05-18 to yesterday: 1 new stats\nThat's all, folks!"


@pytest.mark.parametrize(
    "name", ["nb_uniq_visitors", "nb_uniq_visitors_returning", "nb_uniq_active_visitors", "nb_uniq_engaged_visitors"]
)
def test_get_initial_from_date_in_collect_matomo_stats(db, name):
    # desired datas for sorting test
    StatFactory(period="day", name=name, date="2024-05-17")
    stat = StatFactory(period="day", name=name, date="2024-05-18")

    # undesired datas
    StatFactory(period="xxx", name=name, date="2024-05-19")
    StatFactory(period="day", name="unexpected_name", date="2024-05-20")

    assert get_initial_from_date("day") == stat
