from django.contrib.auth.models import AnonymousUser
from django.db.models import F
from django.forms import HiddenInput
from django.test import TestCase
from faker import Faker
from machina.conf import settings as machina_settings
from machina.core.db.models import get_model

from lacommunaute.forum_conversation.factories import PostFactory, TopicFactory
from lacommunaute.forum_conversation.forms import PostForm


faker = Faker()

Post = get_model("forum_conversation", "Post")


class PostFormTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.topic = TopicFactory(with_post=True)
        cls.user = cls.topic.poster
        cls.forum = cls.topic.forum

    def test_subject_is_hidden(self):
        form = PostForm()
        self.assertIn("subject", form.declared_fields)
        subject = form.declared_fields["subject"]
        self.assertIsInstance(subject.widget, HiddenInput)

    def test_post_subject_comes_from_topic_subject(self):
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
        )
        self.assertTrue(form.is_valid())
        post = form.create_post()
        self.assertEqual(
            post.subject,
            f"{machina_settings.TOPIC_ANSWER_SUBJECT_PREFIX} {self.topic.subject}",
        )

    def test_reply_as_anonymous_user(self):
        post = Post.objects.create(
            topic=self.topic,
            subject=faker.text(max_nb_chars=5),
            content=faker.text(max_nb_chars=5),
            username=faker.email,
            anonymous_key=123,
        )
        form_data = {
            "subject": "subject",
            "content": "content",
            "username": "john@test.com",
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
        self.assertEqual(post.username, "john@test.com")
        self.assertFalse(post.updated_by)
        self.assertEqual(post.updates_count, F("updates_count") + 1)

    def test_reply_as_authenticated_user(self):
        post = PostFactory(topic=self.topic, poster=self.user)
        form_data = {
            "subject": "subject",
            "content": "content",
            "username": "john@test.com",
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
