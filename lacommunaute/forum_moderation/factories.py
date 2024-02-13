import factory
import factory.django
from faker import Faker

from lacommunaute.forum_moderation.models import BlockedDomainName, BlockedEmail


faker = Faker()


class BlockedEmailFactory(factory.django.DjangoModelFactory):
    email = faker.unique.email()
    reason = factory.Faker("sentence", nb_words=5)

    class Meta:
        model = BlockedEmail


class BlockedDomainNameFactory(factory.django.DjangoModelFactory):
    domain = faker.unique.domain_name()
    reason = factory.Faker("sentence", nb_words=5)

    class Meta:
        model = BlockedDomainName
