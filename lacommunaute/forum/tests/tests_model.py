from django.conf import settings
from django.test import TestCase

from lacommunaute.forum.factories import CategoryForumFactory, ForumFactory, ForumRatingFactory
from lacommunaute.forum.models import Forum
from lacommunaute.forum_conversation.factories import TopicFactory
from lacommunaute.users.factories import UserFactory


class ForumModelTest(TestCase):
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

    def test_get_absolute_url(self):
        forum = ForumFactory()
        self.assertEqual(
            forum.get_absolute_url(),
            f"/forum/{forum.slug}-{forum.pk}/",
        )

    def test_upvotes_count(self):
        forum = ForumFactory()
        self.assertEqual(forum.upvotes_count(), 0)
        forum.upvotes.create(voter=UserFactory())
        self.assertEqual(forum.upvotes_count(), 1)

    def test_image_is_imagefield(self):
        forum = ForumFactory()
        self.assertEqual(forum.image.field.__class__.__name__, "ImageField")

    def test_image_url(self):
        forum = ForumFactory(image="test.jpg")
        self.assertEqual(
            forum.image.url.split("?")[0], f"{settings.MEDIA_URL}{settings.AWS_STORAGE_BUCKET_NAME}/{forum.image.name}"
        )
        self.assertIn("AWSAccessKeyId=", forum.image.url)

    def test_is_in_documentation_area(self):
        top_level_category_forum = CategoryForumFactory(with_child=True)
        documentation_forum = top_level_category_forum.children.first()
        sub_documentation_forum = ForumFactory(parent=documentation_forum)

        top_level_forum = ForumFactory()
        forum = ForumFactory(parent=top_level_forum)

        self.assertTrue(top_level_category_forum.is_in_documentation_area)
        self.assertTrue(documentation_forum.is_in_documentation_area)
        self.assertTrue(sub_documentation_forum.is_in_documentation_area)
        self.assertFalse(top_level_forum.is_in_documentation_area)
        self.assertFalse(forum.is_in_documentation_area)

    def test_is_toplevel_discussion_area(self):
        discussion_area_forum = ForumFactory()
        sub_discussion_area_forum = ForumFactory(parent=discussion_area_forum)
        forum = ForumFactory()
        sub_forum = ForumFactory(parent=forum)

        self.assertTrue(discussion_area_forum.is_toplevel_discussion_area)
        self.assertFalse(sub_discussion_area_forum.is_toplevel_discussion_area)
        self.assertFalse(forum.is_toplevel_discussion_area)
        self.assertFalse(sub_forum.is_toplevel_discussion_area)

    def test_get_session_rating(self):
        forum = ForumFactory()
        forum_rating = ForumRatingFactory(forum=forum)

        self.assertIsNone(forum.get_session_rating("test"))
        self.assertEqual(forum.get_session_rating(forum_rating.session_id), forum_rating.rating)

        ForumRatingFactory(forum=forum, session_id=forum_rating.session_id, rating=forum_rating.rating + 1)
        self.assertEqual(forum.get_session_rating(forum_rating.session_id), forum_rating.rating + 1)

    def test_get_average_rating(self):
        forum = ForumFactory()
        ForumRatingFactory(forum=forum, rating=1)
        ForumRatingFactory(forum=forum, rating=5)

        self.assertEqual(forum.get_average_rating(), 3)


class TestForumQueryset:
    def test_get_main_forum_wo_forum(self, db):
        assert Forum.objects.get_main_forum() is None

    def test_get_main_forum_w_several_forums(self, db):
        # level 0
        forums = ForumFactory.create_batch(2)
        # level 1
        ForumFactory(parent=forums[0])
        assert Forum.objects.get_main_forum() == forums[0]
