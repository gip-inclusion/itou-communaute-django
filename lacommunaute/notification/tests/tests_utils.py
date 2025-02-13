import pytest
from django.test import TestCase
from faker import Faker

from lacommunaute.forum.factories import ForumFactory
from lacommunaute.forum_conversation.factories import (
    AnonymousPostFactory,
    AnonymousTopicFactory,
    PostFactory,
    TopicFactory,
)
from lacommunaute.notification.enums import EmailSentTrackKind, NotificationDelay, delay_of_notifications
from lacommunaute.notification.factories import EmailSentTrackFactory, NotificationFactory
from lacommunaute.notification.models import EmailSentTrack, Notification
from lacommunaute.notification.utils import (
    collect_new_users_for_onboarding,
    get_serialized_messages,
    last_notification,
)
from lacommunaute.users.factories import UserFactory
from lacommunaute.users.models import User


faker = Faker()


class LastNotificationTestCase(TestCase):
    def test_email_sent_track_with_kind(self):
        EmailSentTrackFactory(kind="first_reply")
        EmailSentTrackFactory(kind="other")
        self.assertEqual(last_notification(kind="first_reply"), EmailSentTrack.objects.first().created)
        self.assertEqual(last_notification(kind="other"), EmailSentTrack.objects.last().created)


class CollectNewUsersForOnBoardingTestCase(TestCase):
    def test_no_onboarding_notification_ever(self):
        UserFactory()
        self.assertEqual(list(collect_new_users_for_onboarding()), list(User.objects.all()))

    def test_user_against_last_notification(self):
        EmailSentTrackFactory(kind="onboarding")
        UserFactory()
        self.assertEqual(list(collect_new_users_for_onboarding()), list(User.objects.all()))

        EmailSentTrackFactory(kind="onboarding")
        self.assertEqual(len(collect_new_users_for_onboarding()), 0)

    def test_last_emailsenttrack_with_kind(self):
        UserFactory()
        EmailSentTrackFactory(kind="first_reply")
        self.assertEqual(list(collect_new_users_for_onboarding()), list(User.objects.all()))

        EmailSentTrackFactory(kind="onboarding")
        self.assertEqual(len(collect_new_users_for_onboarding()), 0)

    def test_order_by_date_joined(self):
        UserFactory.create_batch(3)
        self.assertEqual(list(collect_new_users_for_onboarding()), list(User.objects.all().order_by("date_joined")))


class TestGetSerializedMessages:
    def test_post_is_topic_head(self, db):
        notification = NotificationFactory(set_post=True)
        assert get_serialized_messages([notification]) == [
            {
                "poster": notification.post.poster_display_name,
                "action": "a posé une nouvelle question",
                "forum": notification.post.topic.forum.name,
                "url": f"{notification.post.topic.get_absolute_url(with_fqdn=True)}?notif={notification.uuid}",
            }
        ]

    def test_post_is_not_topic_head(self, db):
        topic = TopicFactory(with_post=True, answered=True)
        notification = NotificationFactory(post=topic.last_post)
        assert get_serialized_messages([notification]) == [
            {
                "poster": notification.post.poster_display_name,
                "action": f"a répondu à '{notification.post.topic.subject}'",
                "forum": notification.post.topic.forum.name,
                "url": f"{notification.post.topic.get_absolute_url(with_fqdn=True)}?notif={notification.uuid}",
            }
        ]


@pytest.fixture(name="upvoter")
def fixture_upvoter():
    return UserFactory()


@pytest.fixture(name="topic_in_forum_with_upvoter")
def fixture_topic_in_forum_with_upvoter(upvoter):
    return TopicFactory(forum=ForumFactory(upvoted_by=[upvoter]), with_post=True)


class TestCreatePostNotifications:
    def test_pending_topic(self, db, topic_in_forum_with_upvoter, upvoter):
        notification = Notification.objects.get()

        for key, expected in [
            ("recipient", upvoter.email),
            ("post", topic_in_forum_with_upvoter.first_post),
            ("kind", EmailSentTrackKind.PENDING_TOPIC),
            ("delay", NotificationDelay.DAY),
        ]:
            assert getattr(notification, key) == expected

    def test_first_reply(self, db, topic_in_forum_with_upvoter):
        Notification.objects.all().delete()

        PostFactory(topic=topic_in_forum_with_upvoter)
        notification = Notification.objects.get()

        for key, expected in [
            ("recipient", topic_in_forum_with_upvoter.first_post.poster.email),
            ("post", topic_in_forum_with_upvoter.last_post),
            ("kind", EmailSentTrackKind.FIRST_REPLY),
            ("delay", NotificationDelay.ASAP),
        ]:
            assert getattr(notification, key) == expected

    def test_first_reply_on_anonymous_topic(self, db):
        topic = AnonymousTopicFactory(with_post=True)
        Notification.objects.all().delete()

        PostFactory(topic=topic)
        notification = Notification.objects.get()

        for key, expected in [
            ("recipient", topic.first_post.username),
            ("post", topic.last_post),
            ("kind", EmailSentTrackKind.FIRST_REPLY),
            ("delay", NotificationDelay.ASAP),
        ]:
            assert getattr(notification, key) == expected

    def test_following_replies(self, db, topic_in_forum_with_upvoter):
        first_reply_poster = UserFactory()
        PostFactory(topic=topic_in_forum_with_upvoter, poster=first_reply_poster)
        Notification.objects.all().delete()

        PostFactory(topic=topic_in_forum_with_upvoter)

        assert Notification.objects.count() == 2

        for notification in Notification.objects.all():
            assert notification.recipient in [
                topic_in_forum_with_upvoter.first_post.poster.email,
                first_reply_poster.email,
            ]
            for key, expected in [
                ("post", topic_in_forum_with_upvoter.last_post),
                ("kind", EmailSentTrackKind.FOLLOWING_REPLIES),
                ("delay", NotificationDelay.DAY),
            ]:
                assert getattr(notification, key) == expected

    def test_following_replies_on_anonymous_topic(self, db):
        topic = AnonymousTopicFactory(with_post=True)
        post = AnonymousPostFactory(topic=topic)
        Notification.objects.all().delete()

        PostFactory(topic=topic)
        assert Notification.objects.count() == 2

        for notification in Notification.objects.all():
            assert notification.recipient in [topic.first_post.username, post.username]
            for key, expected in [
                ("post", topic.last_post),
                ("kind", EmailSentTrackKind.FOLLOWING_REPLIES),
                ("delay", NotificationDelay.DAY),
            ]:
                assert getattr(notification, key) == expected

    def test_no_notifications_on_unapproved_post(self, db, upvoter):
        topic = TopicFactory(forum=ForumFactory(upvoted_by=[upvoter]))

        for _ in delay_of_notifications:
            PostFactory(topic=topic, approved=False)
            assert Notification.objects.count() == 0
