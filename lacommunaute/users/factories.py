import functools
import random

import factory
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import Group
from machina.core.db.models import get_model


User = get_model("users", "User")

DEFAULT_PASSWORD = "supercalifragilisticexpialidocious"


@functools.cache
def default_password():
    return make_password(DEFAULT_PASSWORD)


class GroupFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Group


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User

    username = factory.LazyAttribute(
        lambda a: "{}_{}_{}".format(a.first_name, a.last_name, random.randrange(111, 999))
    )
    first_name = factory.Faker("first_name")
    last_name = factory.Faker("last_name")
    email = factory.Faker("email")
    password = factory.LazyFunction(default_password)

    @factory.post_generation
    def with_perm(obj, create, extracted, **kwargs):
        if not create or not extracted:
            return
        obj.user_permissions.add(*extracted)
