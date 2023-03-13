from django.core.exceptions import ValidationError
from django.test import TestCase
from django.urls import reverse

from lacommunaute.forum_conversation.factories import TopicFactory
from lacommunaute.forum_conversation.models import Post, Topic


class PostModelTest(TestCase):
    def test_username_is_emailfield(self):
        topic = TopicFactory()
        post = Post(username="not an email", subject="xxx", content="xxx", topic=topic)

        with self.assertRaisesMessage(ValidationError, "Saisissez une adresse de courriel valide."):
            post.full_clean()


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

    def test_topic_type_choices(self):
        self.assertEqual(Topic.TOPIC_POST, 0)
        self.assertEqual(Topic.TOPIC_STICKY, 1)
        self.assertEqual(Topic.TOPIC_ANNOUNCE, 2)
        self.assertEqual(Topic.TOPIC_JOBOFFER, 3)
