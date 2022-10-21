from django.contrib.auth.models import AnonymousUser
from django.db.models import F
from django.test import TestCase
from faker import Faker
from machina.core.db.models import get_model
from machina.test.factories.conversation import PostFactory, create_topic
from machina.test.factories.forum import create_forum

from lacommunaute.forum_conversation.forms import PostForm
from lacommunaute.users.factories import UserFactory


faker = Faker()

Post = get_model("forum_conversation", "Post")


class PostFormTest(TestCase):
    def setUp(self) -> None:
        self.user = UserFactory()
        self.forum = create_forum()
        self.topic = create_topic(forum=self.forum, poster=self.user)

    def test_reply_as_anonymous_user(self):
        post = Post.objects.create(
            topic=self.topic,
            subject=faker.text(max_nb_chars=5),
            content=faker.text(max_nb_chars=5),
            username=faker.name(),
            anonymous_key=123,
        )
        form_data = {
            "subject": "subject",
            "content": "content",
            "username": "testname",
        }
        form = PostForm(
            data=form_data,
            user=AnonymousUser(),
            forum=self.forum,
            topic=self.topic,
            instance=post,
        )
        self.assertTrue(form.is_valid())
        form.update_post(post)
        self.assertEqual(post.username, "testname")
        self.assertFalse(post.updated_by)
        self.assertEqual(post.updates_count, F("updates_count") + 1)

    def test_reply_as_authenticated_user(self):
        post = PostFactory(topic=self.topic, poster=self.user)
        form_data = {
            "subject": "subject",
            "content": "content",
            "username": "testname",
        }
        form = PostForm(
            data=form_data,
            user=self.user,
            forum=self.forum,
            topic=self.topic,
            instance=post,
        )
        form.update_post(post)
        self.assertFalse(post.username)
        self.assertEqual(post.updated_by, self.user)
        self.assertEqual(post.updates_count, F("updates_count") + 1)
