import random
from datetime import UTC

import factory
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import Group

from lacommunaute.users.enums import EmailLastSeenKind, IdentityProvider
from lacommunaute.users.models import EmailLastSeen, User


DEFAULT_PASSWORD = "supercalifragilisticexpialidocious"


class GroupFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Group


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User
        skip_postgeneration_save = True

    username = factory.LazyAttribute(
        lambda a: "{}_{}_{}".format(a.first_name, a.last_name, random.randrange(111, 999))
    )
    first_name = factory.Faker("first_name")
    last_name = factory.Faker("last_name")
    email = factory.Faker("email")
    password = factory.Transformer(DEFAULT_PASSWORD, transform=make_password)
    identity_provider = IdentityProvider.PRO_CONNECT

    class Params:
        for_snapshot = factory.Trait(
            first_name="Adam", last_name="Ondra", email="adam@ondra.com", identity_provider=IdentityProvider.MAGIC_LINK
        )

    @factory.post_generation
    def with_perm(obj, create, extracted, **kwargs):
        if not create or not extracted:
            return
        obj.user_permissions.add(*extracted)


class EmailLastSeenFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = EmailLastSeen

    email = factory.Faker("email")
    last_seen_at = factory.Faker("date_time", tzinfo=UTC)
    last_seen_kind = factory.Iterator(EmailLastSeenKind.choices, getter=lambda c: c[0])

    class Params:
        soft_deleted = factory.Trait(
            deleted_at=factory.Faker("date_time", tzinfo=UTC), email=None, email_hash=factory.Faker("sha256")
        )
