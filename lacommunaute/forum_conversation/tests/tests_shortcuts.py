from django.contrib.auth.models import AnonymousUser
from django.test import TestCase

from lacommunaute.forum_conversation.factories import PostFactory, TopicFactory
from lacommunaute.forum_conversation.shortcuts import (
    get_posts_of_a_topic_except_first_one,
)
from lacommunaute.forum_upvote.factories import UpVoteFactory


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
