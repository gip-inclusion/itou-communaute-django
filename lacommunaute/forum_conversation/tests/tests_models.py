import pytest
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.test import TestCase
from django.urls import reverse

from lacommunaute.forum.factories import ForumFactory
from lacommunaute.forum_conversation.factories import (
    AnonymousPostFactory,
    AnonymousTopicFactory,
    CertifiedPostFactory,
    PostFactory,
    TopicFactory,
)
from lacommunaute.forum_conversation.models import Post, Topic
from lacommunaute.forum_member.shortcuts import get_forum_member_display_name
from lacommunaute.users.enums import EmailLastSeenKind
from lacommunaute.users.factories import UserFactory
from lacommunaute.users.models import EmailLastSeen


@pytest.fixture(name="forum")
def fixture_forum(db):
    return ForumFactory()


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


class TestPostModel:
    @pytest.mark.parametrize(
        "topic", [lambda: TopicFactory(with_post=True), lambda: AnonymousTopicFactory(with_post=True)]
    )
    def test_email_last_seen_when_create(self, db, topic):
        topic = topic()
        email_last_seen = EmailLastSeen.objects.get()
        assert email_last_seen.last_seen_kind == EmailLastSeenKind.POST

        assert email_last_seen.email == topic.poster_email

    @pytest.mark.parametrize(
        "topic", [lambda: TopicFactory(with_post=True), lambda: AnonymousTopicFactory(with_post=True)]
    )
    def test_email_last_seen_when_update(self, db, topic):
        topic = topic()
        EmailLastSeen.objects.all().delete()
        topic.first_post.save()
        assert EmailLastSeen.objects.count() == 0


class TestTopicManager:
    def test_unanswered(self, db, forum):
        TopicFactory(forum=forum, posts_count=0)
        topic = TopicFactory(forum=forum, posts_count=1)
        TopicFactory(forum=forum, posts_count=2)

        TopicFactory(forum=forum, posts_count=1, status=Topic.TOPIC_LOCKED)
        TopicFactory(forum=forum, posts_count=1, type=Topic.TOPIC_ANNOUNCE)
        TopicFactory(forum=forum, posts_count=1, approved=False)

        assert Topic.objects.unanswered().get() == topic

    def test_unanswered_order(self, db, forum):
        topics = TopicFactory.create_batch(size=3, forum=forum, with_post=True)
        expected_date_list = [topic.last_post_on for topic in reversed(topics)]
        extracted_date_list = list(Topic.objects.unanswered().values_list("last_post_on", flat=True))

        assert extracted_date_list == expected_date_list


class TopicManagerTest(TestCase):
    def test_optimized_for_topics_list_disapproved(self):
        TopicFactory(approved=False)
        self.assertEqual(Topic.objects.optimized_for_topics_list(1).count(), 0)

    def test_optimized_for_topics_list_type(self):
        annonce = TopicFactory(type=Topic.TOPIC_ANNOUNCE)
        sticky = TopicFactory(type=Topic.TOPIC_STICKY)
        topic = TopicFactory(type=Topic.TOPIC_POST)
        unapproved_topic = TopicFactory(type=Topic.TOPIC_POST, approved=False)

        qs = Topic.objects.optimized_for_topics_list(1)

        self.assertIn(annonce, qs)
        self.assertIn(sticky, qs)
        self.assertIn(topic, qs)
        self.assertNotIn(unapproved_topic, qs)

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
        self.assertEqual(
            self.topic.get_absolute_url(),
            reverse(
                "forum_conversation:topic",
                kwargs={
                    "forum_pk": self.topic.forum.pk,
                    "forum_slug": self.topic.forum.slug,
                    "pk": self.topic.pk,
                    "slug": self.topic.slug,
                },
            ),
        )
        self.assertEqual(
            self.topic.get_absolute_url(with_fqdn=True),
            f"{settings.COMMU_PROTOCOL}://{settings.COMMU_FQDN}{self.topic.get_absolute_url()}",
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

        post = PostFactory(topic=self.topic, username="user@inclusion.gouv.fr")
        self.assertEqual(post.poster_display_name, "user")

    def test_is_certified(self):
        self.assertFalse(self.topic.is_certified)

        topic = TopicFactory(with_certified_post=True)
        self.assertTrue(topic.is_certified)

    def test_topic_types(self):
        self.assertEqual(0, Topic.TOPIC_POST)
        self.assertEqual(1, Topic.TOPIC_STICKY)
        self.assertEqual(2, Topic.TOPIC_ANNOUNCE)


@pytest.fixture(name="upvoters")
def upvoters_fixture():
    return UserFactory.create_batch(3)


class TestModelMethods:
    def test_forum_upvoters_are_notified_for_new_topic(self, db, upvoters):
        topic = TopicFactory(forum=ForumFactory(upvoted_by=upvoters), with_post=True)
        assert topic.mails_to_notify() == [upvoter.email for upvoter in upvoters]

    def test_forum_upvoters_are_not_notified_on_replies(self, db, upvoters):
        topic = TopicFactory(forum=ForumFactory(upvoted_by=upvoters), with_post=True, answered=True)
        assert not set([upvoter.email for upvoter in upvoters]).intersection(set(topic.mails_to_notify()))

    def test_posts_upvoters_are_notified_on_replies(self, db, upvoters):
        topic = TopicFactory(with_post=True)
        PostFactory(topic=topic, upvoted_by=upvoters)
        assert set([upvoter.email for upvoter in upvoters]).issubset(set(topic.mails_to_notify()))

    def test_authenticated_posters_are_notified_on_replies_except_last_one(self, db):
        topic = TopicFactory(with_post=True)
        PostFactory(topic=topic)
        assert topic.mails_to_notify() == [topic.first_post.poster.email]

    def test_anonymous_posters_are_notified_on_replies_except_last_one(self, db):
        topic = AnonymousTopicFactory(with_post=True)
        AnonymousPostFactory(topic=topic)
        assert topic.mails_to_notify() == [topic.first_post.username]

    def test_notify_replies_deduplication(self, db):
        topic = TopicFactory(with_post=True)
        PostFactory(topic=topic, upvoted_by=[topic.first_post.poster])
        assert topic.mails_to_notify() == [topic.first_post.poster.email]


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
