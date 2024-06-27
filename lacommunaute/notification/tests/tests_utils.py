from django.test import TestCase
from faker import Faker

from lacommunaute.forum_conversation.factories import TopicFactory
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


class GetSeriaizedMessagesTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.topic = TopicFactory(with_post=True)

    def test_get_serialized_messages(self):
        post = self.topic.first_post
        notifications = [NotificationFactory(post=post)]

        serialized_content = get_serialized_messages(notifications)
        self.assertEqual(
            serialized_content,
            [
                {
                    "poster": post.poster_display_name,
                    "action": f"a répondu à '{post.subject}'",
                    "forum": self.topic.forum.name,
                    "url": self.topic.get_absolute_url(with_fqdn=True),
                }
            ],
        )
