from django.db import IntegrityError
from django.test import TestCase

from lacommunaute.forum_conversation.factories import TopicFactory
from lacommunaute.forum_upvote.factories import CertifiedPostFactory
from lacommunaute.forum_upvote.models import UpVote


class UpVoteModelTest(TestCase):
    def test_post_and_voter_are_uniques_together(self):
        topic = TopicFactory(with_post=True)
        UpVote.objects.create(post=topic.first_post, voter=topic.first_post.poster)

        with self.assertRaises(IntegrityError):
            UpVote.objects.create(post=topic.first_post, voter=topic.first_post.poster)


class CertifiedPostModelTest(TestCase):
    def test_topic_is_unique(self):
        topic = TopicFactory(with_certified_post=True)

        with self.assertRaises(IntegrityError):
            CertifiedPostFactory(topic=topic, post=topic.first_post, user=topic.poster)

    def test_post_is_link_to_topic(self):
        topic_to_be_certified = TopicFactory()
        other_topic = TopicFactory(with_post=True)

        with self.assertRaises(ValueError):
            CertifiedPostFactory(
                topic=topic_to_be_certified, post=other_topic.first_post, user=topic_to_be_certified.poster
            )
