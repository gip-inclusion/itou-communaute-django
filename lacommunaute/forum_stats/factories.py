import factory
import factory.django

from lacommunaute.forum_stats.enums import Period
from lacommunaute.forum_stats.models import Stat


class StatFactory(factory.django.DjangoModelFactory):
    date = factory.Faker("date")
    name = factory.Faker("word")
    period = Period.DAY
    value = factory.Faker("pyint")

    class Meta:
        model = Stat
