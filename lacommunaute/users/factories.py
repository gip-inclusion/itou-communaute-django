import random

import factory
from machina.core.db.models import get_model


User = get_model("users", "User")

DEFAULT_PASSWORD = "supercalifragilisticexpialidocious"


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User

    username = factory.LazyAttribute(
        lambda a: "{}_{}_{}".format(a.first_name, a.last_name, random.randrange(111, 999))
    )
    first_name = factory.Faker("first_name")
    last_name = factory.Faker("last_name")
    email = factory.LazyAttribute(lambda a: "{}.{}@neuralia.co".format(a.first_name, a.last_name).lower())
    password = factory.PostGenerationMethodCall("set_password", DEFAULT_PASSWORD)
