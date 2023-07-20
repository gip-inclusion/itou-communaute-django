from django.contrib.auth.models import AnonymousUser
from django.test import TestCase

from lacommunaute.forum.enums import Kind as ForumKind
from lacommunaute.forum.factories import ForumFactory
from lacommunaute.forum_conversation.factories import PostFactory, TopicFactory
from lacommunaute.forum_conversation.shortcuts import can_certify_post, get_posts_of_a_topic_except_first_one
from lacommunaute.forum_upvote.factories import UpVoteFactory
from lacommunaute.users.factories import UserFactory


class GetPostsofaTopicExceptFirstOneTest(TestCase):
    def test_topic_has_no_post(self):
        topic = TopicFactory()
        posts = get_posts_of_a_topic_except_first_one(topic, AnonymousUser())
        self.assertEqual(len(posts), 0)

    def test_topic_has_one_post(self):
        topic = TopicFactory(with_post=True)
        posts = get_posts_of_a_topic_except_first_one(topic, AnonymousUser())

        self.assertEqual(len(posts), 0)

    def test_topic_is_not_approved(self):
        topic = TopicFactory(with_post=True)
        PostFactory(topic=topic, approved=False)
        posts = get_posts_of_a_topic_except_first_one(topic, AnonymousUser())

        self.assertEqual(len(posts), 0)

    def test_topic_has_two_posts_requested_by_anonymous_user(self):
        topic = TopicFactory(with_post=True)
        PostFactory(topic=topic)
        posts = get_posts_of_a_topic_except_first_one(topic, AnonymousUser())
        post = posts.first()

        self.assertEqual(len(posts), 1)
        self.assertEqual(post.upvotes_count, 0)
        self.assertNotIn("has_upvoted", post.__dict__)

    def test_topic_has_two_posts_requested_by_authenticated_user(self):
        topic = TopicFactory(with_post=True)
        PostFactory(topic=topic)
        posts = get_posts_of_a_topic_except_first_one(topic, topic.poster)
        post = posts.first()

        self.assertEqual(len(posts), 1)
        self.assertEqual(post.upvotes_count, 0)
        self.assertFalse(post.has_upvoted)

    def test_topic_has_been_upvoted(self):
        topic = TopicFactory(with_post=True)
        post = PostFactory(topic=topic)
        UpVoteFactory(content_object=post)
        posts = get_posts_of_a_topic_except_first_one(topic, AnonymousUser())
        post = posts.first()

        self.assertEqual(len(posts), 1)
        self.assertEqual(post.upvotes_count, 1)
        self.assertNotIn("has_upvoted", post.__dict__)

    def test_topic_has_been_upvoted_by_the_user(self):
        topic = TopicFactory(with_post=True)
        post = PostFactory(topic=topic)
        UpVoteFactory(content_object=post, voter=topic.poster)
        posts = get_posts_of_a_topic_except_first_one(topic, topic.poster)
        post = posts.first()

        self.assertEqual(len(posts), 1)
        self.assertEqual(post.upvotes_count, 1)
        self.assertTrue(post.has_upvoted)


class CanCertifyPostShortcutTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = UserFactory.create()
        cls.forum = ForumFactory.create()

    def test_user_is_not_authenticated(self):
        self.assertFalse(can_certify_post(self.forum, AnonymousUser()))

    def test_forum_is_private(self):
        self.assertFalse(can_certify_post(ForumFactory.create(kind=ForumKind.PRIVATE_FORUM), self.user))

    def test_forum_is_newsfeed(self):
        self.assertFalse(can_certify_post(ForumFactory.create(kind=ForumKind.NEWS), self.user))

    def test_user_is_not_in_the_forum_members_group(self):
        self.assertFalse(can_certify_post(self.forum, self.user))

    def test_user_is_in_the_forum_members_group(self):
        self.forum.members_group.user_set.add(self.user)
        self.assertTrue(can_certify_post(self.forum, self.user))

    def test_user_is_staff(self):
        self.user.is_staff = True
        self.assertTrue(can_certify_post(self.forum, self.user))
