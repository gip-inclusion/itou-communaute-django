from django.core.exceptions import ValidationError
from django.test import TestCase
from django.urls import reverse

from lacommunaute.forum_conversation.factories import PostFactory, TopicFactory
from lacommunaute.forum_conversation.models import Post
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


class TopicModelTest(TestCase):
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
        topic = TopicFactory(with_post=True)
        self.assertEqual(topic.poster_email, topic.first_post.poster.email)

        topic = TopicFactory()
        post = PostFactory(topic=topic, username="user@beta.gouv.fr")
        self.assertEqual(topic.poster_email, post.username)

    def test_poster_display_name(self):
        topic = TopicFactory(with_post=True)
        self.assertEqual(topic.first_post.poster_display_name, get_forum_member_display_name(topic.first_post.poster))

        post = PostFactory(topic=topic, username="user@beta.gouv.fr")
        self.assertEqual(post.poster_display_name, "user")

    def test_is_certified(self):
        topic = TopicFactory(with_post=True)
        self.assertFalse(topic.is_certified)

        topic = TopicFactory(with_certified_post=True)
        self.assertTrue(topic.is_certified)
