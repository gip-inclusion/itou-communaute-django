from django.test import TestCase
from faker import Faker

from lacommunaute.forum_conversation.factories import PostFactory, TopicFactory
from lacommunaute.notification.factories import EmailSentTrackFactory, NotificationFactory
from lacommunaute.notification.models import EmailSentTrack
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
        topic = TopicFactory(with_post=True)
        notifications = [NotificationFactory(post=topic.first_post)]
        assert get_serialized_messages(notifications) == [
            {
                "poster": topic.first_post.poster_display_name,
                "action": "a posé une nouvelle question",
                "forum": topic.forum.name,
                "url": topic.get_absolute_url(with_fqdn=True),
            }
        ]

    def test_post_is_not_topic_head(self, db):
        post = PostFactory(topic=TopicFactory(with_post=True))
        notifications = [NotificationFactory(post=post)]
        assert get_serialized_messages(notifications) == [
            {
                "poster": post.poster_display_name,
                "action": f"a répondu à '{post.subject}'",
                "forum": post.topic.forum.name,
                "url": post.topic.get_absolute_url(with_fqdn=True),
            }
        ]
