import factory
import factory.django
from machina.test.factories.auth import UserFactory
from machina.test.factories.conversation import PostFactory

from lacommunaute.forum_upvote.models import UpVote


class UpVoteFactory(factory.django.DjangoModelFactory):
    voter = factory.SubFactory(UserFactory)
    post = factory.SubFactory(PostFactory)

    class Meta:
        model = UpVote
