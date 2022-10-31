from django.core.exceptions import ValidationError
from django.test import TestCase
from django.urls import reverse
from machina.test.factories.conversation import create_topic
from machina.test.factories.forum import create_forum

from lacommunaute.forum_conversation.models import Post
from lacommunaute.users.factories import UserFactory


class PostModelTest(TestCase):
    def test_username_is_emailfield(self):
        topic = create_topic(forum=create_forum(), poster=UserFactory())
        post = Post(username="not an email", subject="xxx", content="xxx", topic=topic)

        with self.assertRaisesMessage(ValidationError, "Saisissez une adresse de courriel valide."):
            post.full_clean()


class TopicModelTest(TestCase):
    def test_get_absolute_url(self):
        topic = create_topic(forum=create_forum(), poster=UserFactory())
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
