import random

import factory
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import Group

from lacommunaute.users.models import User


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

    @factory.post_generation
    def with_perm(obj, create, extracted, **kwargs):
        if not create or not extracted:
            return
        obj.user_permissions.add(*extracted)
