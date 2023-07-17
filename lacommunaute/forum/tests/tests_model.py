from django.db import IntegrityError
from django.test import TestCase

from lacommunaute.forum.enums import Kind as ForumKind
from lacommunaute.forum.factories import ForumFactory
from lacommunaute.forum.models import Forum
from lacommunaute.forum_conversation.factories import TopicFactory


class ForumManagerTest(TestCase):
    def test_public_method(self):
        forum = ForumFactory(kind=ForumKind.PUBLIC_FORUM)
        ForumFactory(kind=ForumKind.NEWS)
        ForumFactory(kind=ForumKind.PRIVATE_FORUM)
        self.assertEqual(forum, Forum.objects.public().get())


class ForumModelTest(TestCase):
    def test_invitation_token_is_unique(self):
        forum = ForumFactory()

        with self.assertRaises(IntegrityError):
            forum.id = None
            forum.save()

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

    def test_kind(self):
        self.assertEqual(
            Forum.kind.field.flatchoices,
            [("PUBLIC_FORUM", "Espace public"), ("PRIVATE_FORUM", "Espace privé"), ("NEWS", "Actualités")],
        )

    def test_get_absolute_url(self):
        forum = ForumFactory()
        self.assertEqual(
            forum.get_absolute_url(),
            f"/forum/{forum.slug}-{forum.pk}/",
        )
