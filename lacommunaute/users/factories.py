import factory
from machina.core.db.models import get_model


User = get_model("users", "User")

DEFAULT_PASSWORD = "supercalifragilisticexpialidocious"


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User

    first_name = factory.Faker("first_name")
    last_name = factory.Faker("last_name")
    email = factory.Sequence("user{0}@neuralia.co".format)
    password = factory.PostGenerationMethodCall("set_password", DEFAULT_PASSWORD)
