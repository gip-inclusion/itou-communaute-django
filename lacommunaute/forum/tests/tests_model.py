from django.db import IntegrityError
from django.test import TestCase
from django.utils import timezone
from faker import Faker
from machina.core.db.models import get_model
from machina.core.loading import get_class

from lacommunaute.forum.factories import ForumFactory
from lacommunaute.forum.models import Forum
from lacommunaute.forum_conversation.factories import PostFactory, TopicFactory
from lacommunaute.forum_conversation.forum_polls.factories import TopicPollVoteFactory
from lacommunaute.forum_upvote.factories import UpVoteFactory


faker = Faker()

ForumPermission = get_model("forum_permission", "ForumPermission")
UserForumPermission = get_model("forum_permission", "UserForumPermission")
PermissionHandler = get_class("forum_permission.handler", "PermissionHandler")
assign_perm = get_class("forum_permission.shortcuts", "assign_perm")
remove_perm = get_class("forum_permission.shortcuts", "remove_perm")


class ForumManagerTest(TestCase):
    def test_private_forum(self):
        ForumFactory(is_private=True)
        self.assertEqual(Forum.objects.public().count(), 0)

    def test_public_forum(self):
        forum = ForumFactory(is_private=False)
        self.assertEqual(Forum.objects.public().count(), 1)
        self.assertIn(forum, Forum.objects.public())


class ForumModelTest(TestCase):
    def test_invitation_token_is_unique(self):
        forum = ForumFactory()

        with self.assertRaises(IntegrityError):
            forum.id = None
            forum.save()

    def test_get_stats(self):

        forum = ForumFactory()
        topic = TopicFactory(forum=forum, with_post=True, with_poll_vote=True)
        UpVoteFactory(post=topic.posts.first(), voter=topic.poster)

        # create old instance to ensure they are filtered
        fifteen_days_ago = timezone.now() - timezone.timedelta(days=15)
        old_topic = TopicFactory(forum=forum)
        old_topic.created = fifteen_days_ago
        old_topic.save()
        old_post = PostFactory(topic=old_topic, poster=old_topic.poster)
        old_post.created = fifteen_days_ago
        old_post.save()
        old_pollvote = TopicPollVoteFactory(voter=old_topic.poster, poll_option__poll__topic=old_topic)
        old_pollvote.timestamp = fifteen_days_ago
        old_pollvote.save()
        old_upvote = UpVoteFactory(post=old_topic.posts.first(), voter=old_topic.poster)
        old_upvote.created_at = fifteen_days_ago
        old_upvote.save()

        # create fake forum to ensure post, topic, etc… number is filter by forum
        fake_forum = ForumFactory()
        fake_topic = TopicFactory(forum=fake_forum, with_post=True, with_poll_vote=True)
        UpVoteFactory(post=fake_topic.posts.first(), voter=fake_topic.poster)

        self.assertEqual(
            forum.get_stats(1),
            {
                "period": [timezone.now().strftime("%Y-%W")],
                "pollvotes": [1],
                "upvotes": [1],
                "posts": [1],
                "topics": [1],
            },
        )

    def test_get_unanswered_topics(self):
        topic1 = TopicFactory(forum=ForumFactory(), posts_count=1)
        topic2 = TopicFactory(forum=ForumFactory(parent=topic1.forum), posts_count=1)
        TopicFactory(forum=ForumFactory(), posts_count=1)

        unanswered_topics = topic1.forum.get_unanswered_topics()
        self.assertEqual(unanswered_topics.count(), 2)
        self.assertIn(topic1, unanswered_topics)
        self.assertIn(topic2, unanswered_topics)

    def test_count_unanswered_topics(self):
        topic = TopicFactory(forum=ForumFactory(), posts_count=1)
        TopicFactory(forum=ForumFactory(parent=topic.forum), posts_count=1)
        self.assertEqual(topic.forum.count_unanswered_topics, 2)