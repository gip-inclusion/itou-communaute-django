from django.db import IntegrityError
from django.test import TestCase

from lacommunaute.forum_conversation.factories import TopicFactory
from lacommunaute.forum_upvote.models import UpVote


class UpVoteModelTest(TestCase):
    def test_post_and_voter_are_uniques_together(self):
        topic = TopicFactory(with_post=True)
        UpVote.objects.create(post=topic.first_post, voter=topic.first_post.poster)

        with self.assertRaises(IntegrityError):
            UpVote.objects.create(post=topic.first_post, voter=topic.first_post.poster)
