import random
from datetime import UTC

import factory
from dateutil.relativedelta import relativedelta
from django.conf import settings
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import Group
from django.utils import timezone

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
    email = factory.Sequence("email{}@domain.com".format)
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

    @factory.post_generation
    def is_in_staff_group(obj, create, extracted, **kwargs):
        if not create or not extracted:
            return
        obj.groups.add(Group.objects.get(name=settings.STAFF_GROUP_NAME))
        obj.is_staff = True
        obj.save()


class EmailLastSeenFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = EmailLastSeen

    email = factory.Sequence("email{}@domain.com".format)
    last_seen_at = factory.Faker("date_time", tzinfo=UTC)
    last_seen_kind = factory.Iterator(EmailLastSeenKind.choices, getter=lambda c: c[0])
    missyou_send_at = None
    deleted_at = None

    class Params:
        soft_deleted = factory.Trait(
            missyou_send_at=factory.Faker("date_time", tzinfo=UTC),
            deleted_at=factory.Faker("date_time", tzinfo=UTC),
            email_hash=factory.Faker("sha256"),
        )
        missyou_sent = factory.Trait(missyou_send_at=factory.Faker("date_time", tzinfo=UTC))
        soft_deletable = factory.Trait(
            missyou_send_at=timezone.now() - relativedelta(days=30),
            deleted_at=None,
        )
