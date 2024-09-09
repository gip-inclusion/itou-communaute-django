import datetime

import factory
import factory.django

from lacommunaute.forum.factories import ForumFactory
from lacommunaute.stats.enums import Period
from lacommunaute.stats.models import ForumStat, Stat


class StatFactory(factory.django.DjangoModelFactory):
    date = factory.Faker("date")
    name = factory.Faker("word")
    period = Period.DAY
    value = factory.Faker("pyint")

    class Meta:
        model = Stat

    class Params:
        for_dsp_snapshot = factory.Trait(
            date=datetime.date(2024, 5, 17),
            name="dsp",
            value=46,
            period="day",
        )


class ForumStatFactory(factory.django.DjangoModelFactory):
    date = factory.Faker("date")
    period = Period.DAY
    forum = factory.SubFactory(ForumFactory)
    visits = factory.Faker("pyint")
    entry_visits = factory.Faker("pyint")
    time_spent = factory.Faker("pyint")

    class Meta:
        model = ForumStat

    class Params:
        for_snapshot = factory.Trait(period="week", date=datetime.date(2024, 5, 20))
        for_snapshot_older = factory.Trait(period="week", date=datetime.date(2024, 5, 13))
