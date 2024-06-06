import pytest  # noqa

from django.core.management import call_command
from lacommunaute.surveys.factories import DSPFactory
from lacommunaute.forum_stats.factories import StatFactory


def test_collect_django_stats(db, capsys):
    DSPFactory()
    StatFactory(for_dsp_snapshot=True)
    call_command("collect_django_stats")
    captured = capsys.readouterr()
    assert captured.out.strip() == "Collecting DSP stats from 2024-05-18 to yesterday: 1 new stats\nThat's all, folks!"
