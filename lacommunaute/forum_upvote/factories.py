import factory
import factory.django

from lacommunaute.forum_upvote.models import CertifiedPost, UpVote


class UpVoteFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = UpVote


class CertifiedPostFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = CertifiedPost
