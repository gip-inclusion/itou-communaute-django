import pytest
from django.db import IntegrityError

from lacommunaute.forum_conversation.factories import TopicFactory
from lacommunaute.forum_upvote.models import UpVote


class TestUpVoteModel:
    def test_generic_relation(self, db):
        topic = TopicFactory(with_post=True)
        UpVote.objects.create(content_object=topic.first_post, voter=topic.first_post.poster)
        UpVote.objects.create(content_object=topic.forum, voter=topic.first_post.poster)

        assert UpVote.objects.count() == 2

    def test_upvoted_post_unicity(self, db):
        topic = TopicFactory(with_post=True)
        UpVote.objects.create(content_object=topic.first_post, voter=topic.first_post.poster)

        with pytest.raises(IntegrityError):
            UpVote.objects.create(content_object=topic.first_post, voter=topic.first_post.poster)

    def test_upvoted_forum_unicity(self, db):
        topic = TopicFactory(with_post=True)
        UpVote.objects.create(content_object=topic.forum, voter=topic.first_post.poster)

        with pytest.raises(IntegrityError):
            UpVote.objects.create(content_object=topic.forum, voter=topic.first_post.poster)
