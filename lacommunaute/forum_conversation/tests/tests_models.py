from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.test import TestCase
from django.urls import reverse

from lacommunaute.forum.factories import ForumFactory
from lacommunaute.forum_conversation.factories import CertifiedPostFactory, PostFactory, TopicFactory
from lacommunaute.forum_conversation.models import Post, Topic
from lacommunaute.forum_member.shortcuts import get_forum_member_display_name


class PostModelTest(TestCase):
    def test_username_is_emailfield(self):
        topic = TopicFactory()
        post = Post(username="not an email", subject="xxx", content="xxx", topic=topic)

        with self.assertRaisesMessage(ValidationError, "Saisissez une adresse de courriel valide."):
            post.full_clean()

    def test_is_certified(self):
        topic = TopicFactory(with_post=True)
        self.assertFalse(topic.last_post.is_certified)

        topic = TopicFactory(with_certified_post=True)
        self.assertTrue(topic.last_post.is_certified)


class TopicManagerTest(TestCase):
    def test_unanswered(self):
        forum = ForumFactory()

        TopicFactory(forum=forum, posts_count=0)
        topic = TopicFactory(forum=forum, posts_count=1)
        TopicFactory(forum=forum, posts_count=2)

        TopicFactory(forum=forum, posts_count=1, status=Topic.TOPIC_LOCKED)
        TopicFactory(forum=forum, posts_count=1, type=Topic.TOPIC_ANNOUNCE)
        TopicFactory(forum=forum, posts_count=1, approved=False)

        self.assertEqual(Topic.objects.unanswered().get(), topic)

    def test_optimized_for_topics_list_disapproved(self):
        TopicFactory(approved=False)
        self.assertEqual(Topic.objects.optimized_for_topics_list(1).count(), 0)

    def test_optimized_for_topics_list_type(self):
        annonce = TopicFactory(type=Topic.TOPIC_ANNOUNCE)
        sticky = TopicFactory(type=Topic.TOPIC_STICKY)
        topic = TopicFactory(type=Topic.TOPIC_POST)

        qs = Topic.objects.optimized_for_topics_list(1)

        self.assertNotIn(annonce, qs)
        self.assertIn(sticky, qs)
        self.assertIn(topic, qs)

    def test_optimized_for_topics_list_likes(self):
        topic = TopicFactory(with_post=True)

        instance = Topic.objects.optimized_for_topics_list(topic.poster.id).first()

        self.assertEqual(instance.likes, 0)
        self.assertEqual(False, instance.has_liked)

        topic.likers.add(topic.poster)

        instance = Topic.objects.optimized_for_topics_list(topic.poster.id).first()

        self.assertEqual(instance.likes, 1)
        self.assertEqual(True, instance.has_liked)

    def test_optimized_for_topics_list_order(self):
        topic1 = TopicFactory(with_post=True)
        topic2 = TopicFactory(with_post=True)

        qs = Topic.objects.optimized_for_topics_list(1)

        self.assertEqual(qs.first(), topic2)
        self.assertEqual(qs.last(), topic1)

        PostFactory(topic=topic1)
        self.assertEqual(qs.first(), topic1)
        self.assertEqual(qs.last(), topic2)


class TopicModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.topic = TopicFactory(with_post=True)

    def test_get_absolute_url(self):
        topic = TopicFactory()
        self.assertEqual(
            topic.get_absolute_url(),
            reverse(
                "forum_conversation:topic",
                kwargs={
                    "forum_pk": topic.forum.pk,
                    "forum_slug": topic.forum.slug,
                    "pk": topic.pk,
                    "slug": topic.slug,
                },
            ),
        )

    def test_poster_email(self):
        self.assertEqual(self.topic.poster_email, self.topic.first_post.poster.email)

        anonymous_topic = TopicFactory()
        anonymous_post = AnonymousPostFactory(topic=anonymous_topic)
        self.assertEqual(anonymous_topic.poster_email, anonymous_post.username)

    def test_poster_display_name(self):
        self.assertEqual(
            self.topic.first_post.poster_display_name, get_forum_member_display_name(self.topic.first_post.poster)
        )

        post = PostFactory(topic=self.topic, username="user@beta.gouv.fr")
        self.assertEqual(post.poster_display_name, "user")

    def test_is_certified(self):
        self.assertFalse(self.topic.is_certified)

        topic = TopicFactory(with_certified_post=True)
        self.assertTrue(topic.is_certified)

    def test_topic_types(self):
        self.assertEqual(0, Topic.TOPIC_POST)
        self.assertEqual(1, Topic.TOPIC_STICKY)
        self.assertEqual(2, Topic.TOPIC_ANNOUNCE)


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
