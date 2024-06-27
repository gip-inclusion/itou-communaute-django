import factory
from faker import Faker

from lacommunaute.edito.models import Edito
from lacommunaute.users.factories import UserFactory


faker = Faker()


class EditoFactory(factory.django.DjangoModelFactory):
    poster = factory.SubFactory(UserFactory)
    title = faker.sentence()
    content = faker.text()
    url = faker.url()
    link_title = faker.sentence()

    class Meta:
        model = Edito

    class Params:
        for_snapshot = factory.Trait(
            title="Snapshot title",
            content="Snapshot *content*",
            url="https://example.com",
            link_title="Snapshot link title",
        )
