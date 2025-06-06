import pytest
from django.conf import settings
from django.forms import HiddenInput
from django.test import TestCase
from django.urls import reverse
from faker import Faker
from taggit.models import Tag

from lacommunaute.forum.factories import ForumFactory
from lacommunaute.forum_conversation.factories import (
    AnonymousPostFactory,
    AnonymousTopicFactory,
    PostFactory,
    TopicFactory,
)
from lacommunaute.forum_conversation.forms import PostForm
from lacommunaute.forum_conversation.models import Topic
from lacommunaute.users.factories import UserFactory


faker = Faker(settings.LANGUAGE_CODE)


class PostFormTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.topic = TopicFactory(with_post=True)
        cls.user = cls.topic.poster
        cls.forum = cls.topic.forum
        cls.form_data = {"subject": faker.text(max_nb_chars=10), "content": faker.paragraph(nb_sentences=5)}

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
            self.topic.subject,
        )


@pytest.fixture(name="forum")
def fixture_forum():
    return ForumFactory()


def get_create_topic_url(forum):
    return reverse("forum_conversation:topic_create", kwargs={"forum_pk": forum.pk, "forum_slug": forum.slug})


def get_update_topic_url(topic):
    return reverse(
        "forum_conversation:topic_update",
        kwargs={"forum_slug": topic.forum.slug, "forum_pk": topic.forum.pk, "pk": topic.pk, "slug": topic.slug},
    )


def get_reply_topic_url(topic):
    return reverse(
        "forum_conversation_extension:post_create",
        kwargs={"forum_slug": topic.forum.slug, "forum_pk": topic.forum.pk, "pk": topic.pk, "slug": topic.slug},
    )


def get_post_update_url(post):
    return reverse(
        "forum_conversation:post_update",
        kwargs={
            "forum_slug": post.topic.forum.slug,
            "forum_pk": post.topic.forum.pk,
            "topic_pk": post.topic.pk,
            "topic_slug": post.topic.slug,
            "pk": post.pk,
        },
    )


superuser_hidden_fields = {
    "poll-TOTAL_FORMS": 2,
    "poll-INITIAL_FORMS": 0,
    "attachment-TOTAL_FORMS": 1,
    "attachment-INITIAL_FORMS": 0,
}


class TestTopicForm:
    def test_create_topic_as_anonymous(self, db, client, forum):
        username = faker.email()

        response = client.post(
            get_create_topic_url(forum),
            data={"subject": "Test", "content": faker.paragraph(nb_sentences=5), "username": username},
        )
        assert response.status_code == 302

        topic = Topic.objects.get()
        assert topic.first_post.username == username
        assert topic.poster is None
        assert topic.first_post.poster is None
        assert topic.first_post.updates_count == 0
        assert topic.first_post.updated_by is None

    def test_update_anonymous_topic_as_self(self, db, client, forum):
        topic = AnonymousTopicFactory(forum=forum, with_post=True)
        username = topic.first_post.username
        session = client.session
        session["anonymous_topic"] = topic.first_post.anonymous_key

        data = {"subject": faker.word(), "content": faker.paragraph(nb_sentences=5), "username": username}
        response = client.post(get_update_topic_url(topic), data=data)
        assert response.status_code == 302

        topic.refresh_from_db()
        assert topic.first_post.username == username
        assert topic.poster is None
        assert topic.first_post.poster is None
        assert topic.first_post.updates_count == 0  # surprisingly, this is not incremented
        assert topic.first_post.updated_by is None  # updated_by is a FK on User

    def test_update_anonymous_topic_as_superuser(self, db, client, forum):
        topic = AnonymousTopicFactory(forum=forum, with_post=True)
        username = topic.first_post.username
        superuser = UserFactory(is_superuser=True)
        client.force_login(superuser)

        data = {
            "subject": faker.word(),
            "content": faker.paragraph(nb_sentences=5),
            **superuser_hidden_fields,
        }
        response = client.post(get_update_topic_url(topic), data=data)
        assert response.status_code == 302

        topic.refresh_from_db()
        assert topic.first_post.username == username
        assert topic.poster is None
        assert topic.first_post.poster is None
        assert topic.first_post.updated_by == superuser

    def test_create_topic_as_authenticated(self, db, client, forum):
        user = UserFactory()
        client.force_login(user)

        response = client.post(
            get_create_topic_url(forum), data={"subject": "Test", "content": faker.paragraph(nb_sentences=5)}
        )
        assert response.status_code == 302

        topic = Topic.objects.get()
        assert topic.poster == user
        assert topic.first_post.poster == user
        assert topic.first_post.username is None
        assert topic.first_post.updates_count == 0
        assert topic.first_post.updated_by is None

    def test_update_authenticated_topic_as_self(self, db, client, forum):
        topic = TopicFactory(forum=forum, with_post=True)
        user = topic.poster
        client.force_login(user)

        data = {"subject": faker.word(), "content": faker.paragraph(nb_sentences=5)}
        response = client.post(get_update_topic_url(topic), data=data)
        assert response.status_code == 302

        topic.refresh_from_db()
        assert topic.first_post.username is None
        assert topic.poster == user
        assert topic.first_post.poster == user
        assert topic.first_post.updated_by == user

    def test_update_authenticated_topic_as_superuser(self, db, client, forum):
        topic = TopicFactory(forum=forum, with_post=True)
        user = topic.poster
        superuser = UserFactory(is_superuser=True)
        client.force_login(superuser)

        data = {
            "subject": faker.word(),
            "content": faker.paragraph(nb_sentences=5),
            **superuser_hidden_fields,
        }
        response = client.post(get_update_topic_url(topic), data=data)
        assert response.status_code == 302

        topic.refresh_from_db()
        assert topic.first_post.username is None
        assert topic.poster == user
        assert topic.first_post.poster == user
        assert topic.first_post.updated_by == superuser

    def test_init_tags_when_creating_topic(self, db, client, forum):
        response = client.get(get_create_topic_url(forum))
        assert response.status_code == 200
        assert response.context_data["post_form"].fields["tags"].initial is None

    def test_init_tags_when_updating_topic(self, db, client, forum):
        topic = TopicFactory(forum=forum, with_post=True)
        client.force_login(topic.poster)
        response = client.get(get_update_topic_url(topic))
        assert response.status_code == 200
        assert set(response.context_data["post_form"].fields["tags"].initial) == set(Tag.objects.none())

    def test_init_tags_when_updating_tagged_topic(self, db, client, forum):
        topic = TopicFactory(forum=forum, with_post=True, with_tags=[faker.word() for _ in range(2)])
        client.force_login(topic.poster)

        response = client.get(get_update_topic_url(topic))
        assert response.status_code == 200
        assert set(response.context_data["post_form"].fields["tags"].initial) == set(Tag.objects.all())


class TestPostForm:
    def test_reply_as_anonymous(self, db, client, forum):
        topic = TopicFactory(forum=forum, with_post=True)
        username = faker.email()

        response = client.post(
            get_reply_topic_url(topic), data={"content": faker.paragraph(nb_sentences=5), "username": username}
        )
        assert response.status_code == 200  # htmx view

        topic.refresh_from_db()
        post = topic.posts.last()
        assert post.username == username
        assert post.poster is None
        assert post.updates_count == 0
        assert post.updated_by is None

    def test_update_anonymous_reply_as_self(self, db, client, forum):
        post = AnonymousPostFactory(topic=TopicFactory(forum=forum, with_post=True))
        username = post.username
        session = client.session
        session["anonymous_post"] = post.anonymous_key

        data = {"content": faker.paragraph(nb_sentences=5), "username": username}
        response = client.post(get_post_update_url(post), data=data)
        assert response.status_code == 302

        post.refresh_from_db()
        assert post.username == username
        assert post.poster is None
        assert post.updates_count == 0  # surprisingly, this is not incremented
        assert post.updated_by is None

    def test_update_anonymous_reply_as_superuser(self, db, client, forum):
        post = AnonymousPostFactory(topic=TopicFactory(forum=forum, with_post=True))
        username = post.username
        superuser = UserFactory(is_superuser=True)
        client.force_login(superuser)

        data = {"content": faker.paragraph(nb_sentences=5), **superuser_hidden_fields}
        response = client.post(get_post_update_url(post), data=data)
        assert response.status_code == 302

        post.refresh_from_db()
        assert post.username == username
        assert post.poster is None
        assert post.updates_count == 1
        assert post.updated_by == superuser

    def test_reply_as_authenticated(self, db, client, forum):
        topic = TopicFactory(forum=forum, with_post=True)
        user = UserFactory()
        client.force_login(user)

        response = client.post(get_reply_topic_url(topic), data={"content": faker.paragraph(nb_sentences=5)})
        assert response.status_code == 200

        topic.refresh_from_db()
        assert topic.posts.count() == 2

        post = topic.posts.last()
        assert post.username is None
        assert post.poster == user
        assert post.updates_count == 0
        assert post.updated_by is None

    def test_update_authenticated_reply_as_self(self, db, client, forum):
        post = PostFactory(topic=TopicFactory(forum=forum, with_post=True))
        user = post.poster
        client.force_login(user)

        data = {"content": faker.paragraph(nb_sentences=5)}
        response = client.post(get_post_update_url(post), data=data)
        assert response.status_code == 302

        post.refresh_from_db()
        assert post.username is None
        assert post.poster == user
        assert post.updates_count == 1
        assert post.updated_by == user

    def test_update_authenticated_reply_as_superuser(self, db, client, forum):
        post = PostFactory(topic=TopicFactory(forum=forum, with_post=True))
        user = post.poster
        superuser = UserFactory(is_superuser=True)
        client.force_login(superuser)

        data = {"content": faker.paragraph(nb_sentences=5), **superuser_hidden_fields}
        response = client.post(get_post_update_url(post), data=data)
        assert response.status_code == 302

        post.refresh_from_db()
        assert post.username is None
        assert post.poster == user
        assert post.updates_count == 1
        assert post.updated_by == superuser
