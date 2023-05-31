from django.conf import settings
from django.test import TestCase
from faker import Faker

from lacommunaute.forum_conversation.factories import PostFactory, TopicFactory
from lacommunaute.notification.factories import BouncedEmailFactory, EmailSentTrackFactory
from lacommunaute.notification.models import EmailSentTrack
from lacommunaute.notification.utils import (
    collect_first_replies,
    collect_new_users_for_onboarding,
    last_notification,
    should_not_be_approved,
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


class CollectFirstRepliesTestCase(TestCase):
    @classmethod
    def setUp(cls):
        cls.topic = TopicFactory(with_post=True)

    def test_no_reply_ever(self):
        post = PostFactory(topic=self.topic)
        self.assertEqual(
            collect_first_replies(),
            [
                (
                    f"{settings.COMMU_PROTOCOL}://{settings.COMMU_FQDN}{post.topic.get_absolute_url()}",
                    post.topic.subject,
                    post.topic.poster_email,
                    post.poster_display_name,
                )
            ],
        )

    def test_no_reply_since_last_notification(self):
        PostFactory(topic=self.topic)
        EmailSentTrackFactory(kind="first_reply")

        self.assertEqual(len(collect_first_replies()), 0)

    def test_replies_since_last_notification(self):
        EmailSentTrackFactory(kind="first_reply")
        post = PostFactory(topic=self.topic)

        self.assertEqual(
            collect_first_replies(),
            [
                (
                    f"{settings.COMMU_PROTOCOL}://{settings.COMMU_FQDN}{post.topic.get_absolute_url()}",
                    post.topic.subject,
                    post.topic.poster_email,
                    post.poster_display_name,
                )
            ],
        )

    def test_unapproved_reply_in_previous_hour(self):
        PostFactory(topic=self.topic, approved=False)
        self.assertEqual(len(collect_first_replies()), 0)

    def test_last_emailsenttrack_with_kind(self):
        PostFactory(topic=self.topic)
        EmailSentTrackFactory(kind="other")

        self.assertEqual(len(collect_first_replies()), 1)

        EmailSentTrackFactory(kind="first_reply")

        self.assertEqual(len(collect_first_replies()), 0)


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


class ShouldNotBeApprovedTestCase(TestCase):
    def test_is_bounced_email(self):
        email = faker.email()
        self.assertFalse(should_not_be_approved(email))

        BouncedEmailFactory(email=email)
        self.assertTrue(should_not_be_approved(email))

    def test_email_is_whitelisted_even_if_bounced(self):
        email = faker.email()
        UserFactory(email=email)
        self.assertFalse(should_not_be_approved(email))

        BouncedEmailFactory(email=email)
        self.assertFalse(should_not_be_approved(email))
