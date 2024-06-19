import datetime

import factory
import factory.django

from lacommunaute.stats.enums import Period
from lacommunaute.stats.models import Stat


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
