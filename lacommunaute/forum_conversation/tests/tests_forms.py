from django.db.models import F
from django.forms import HiddenInput
from django.test import TestCase
from faker import Faker
from machina.conf import settings as machina_settings

from lacommunaute.forum_conversation.factories import PostFactory, TopicFactory
from lacommunaute.forum_conversation.forms import PostForm


faker = Faker()


class PostFormTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.topic = TopicFactory(with_post=True)
        cls.user = cls.topic.poster
        cls.forum = cls.topic.forum
        cls.form_data = {"subject": faker.text(max_nb_chars=10), "content": faker.text(max_nb_chars=30)}

    def test_subject_is_hidden(self):
        form = PostForm()
        self.assertIn("subject", form.declared_fields)
        subject = form.declared_fields["subject"]
        self.assertIsInstance(subject.widget, HiddenInput)

    def test_post_subject_comes_from_topic_subject(self):
        form = PostForm(
            data=self.form_data,
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

    def test_reply_as_authenticated_user(self):
        post = PostFactory(topic=self.topic, poster=self.user)
        form = PostForm(
            data=self.form_data,
            user=self.user,
            forum=self.forum,
            topic=self.topic,
            instance=post,
        )
        form.update_post(post)
        self.assertFalse(post.username)
        self.assertEqual(post.updated_by, self.user)
        self.assertEqual(post.updates_count, F("updates_count") + 1)
