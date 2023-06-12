import factory
from faker import Faker

from lacommunaute.event.models import Event
from lacommunaute.users.factories import UserFactory


faker = Faker()


class EventFactory(factory.django.DjangoModelFactory):
    poster = factory.SubFactory(UserFactory)
    name = factory.Faker("name")
    date = faker.future_datetime().date()
    time = faker.time_object()
    end_date = factory.LazyAttribute(lambda o: o.date)
    end_time = factory.LazyAttribute(lambda o: o.time.replace(hour=(o.time.hour + 1) % 24))
    location = faker.url()
    description = faker.text(max_nb_chars=200)

    class Meta:
        model = Event
