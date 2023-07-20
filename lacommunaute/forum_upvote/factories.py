import factory
import factory.django

from lacommunaute.forum_upvote.models import UpVote


class UpVoteFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = UpVote
