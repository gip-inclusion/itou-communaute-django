import datetime

import factory
import factory.django
from django.conf import settings

from lacommunaute.forum_stats.enums import Period
from lacommunaute.forum_stats.models import SearchCollectionPeriod, SearchQuery, Stat


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


class SearchCollectionPeriodFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = SearchCollectionPeriod

    name = factory.Faker("word")
    start_date = factory.Faker("date")

    @factory.lazy_attribute
    def end_date(self):
        return (
            datetime.datetime.strptime(self.start_date, "%Y-%m-%d")
            + datetime.timedelta(days=settings.SEARCH_COLLECTION_PERIOD_DAYS)
        ).date()


class SearchQueryFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = SearchQuery

    label = factory.Faker("word")
    period = factory.SubFactory(SearchCollectionPeriodFactory)
    nb_visits = factory.Faker("random_int", min=1, max=10)
