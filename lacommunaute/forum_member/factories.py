import factory
from machina.core.db.models import get_model

from lacommunaute.users.factories import UserFactory


ForumProfile = get_model("forum_member", "ForumProfile")


class ForumProfileFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = ForumProfile

    user = factory.SubFactory(UserFactory)
    signature = factory.Faker("sentence", nb_words=40)
