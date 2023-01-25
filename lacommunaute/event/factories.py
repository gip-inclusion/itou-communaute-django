import datetime

import factory
from factory import fuzzy
from faker import Faker

from lacommunaute.event.models import Event
from lacommunaute.users.factories import UserFactory


faker = Faker()


class EventFactory(factory.django.DjangoModelFactory):
    poster = factory.SubFactory(UserFactory)
    name = factory.Faker("name")
    date = fuzzy.FuzzyDate(datetime.date(2023, 5, 17), datetime.date(2023, 7, 16))
    time = datetime.time(10)
    end_date = factory.LazyAttribute(lambda o: o.date)
    end_time = factory.LazyAttribute(lambda o: o.time.replace(hour=(o.time.hour + 1) % 24))
    location = faker.url()
    description = factory.LazyAttribute(lambda t: faker.text(max_nb_chars=200))

    class Meta:
        model = Event
