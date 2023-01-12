import factory

from lacommunaute.forum_member.models import ForumProfile
from lacommunaute.users.factories import UserFactory


class ForumProfileFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = ForumProfile

    user = factory.SubFactory(UserFactory)
    signature = factory.Faker("sentence", nb_words=40)
