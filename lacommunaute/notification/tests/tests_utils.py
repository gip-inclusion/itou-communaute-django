from django.test import TestCase
from faker import Faker

from lacommunaute.forum_conversation.factories import PostFactory, TopicFactory
from lacommunaute.forum_conversation.models import Post
from lacommunaute.notification.enums import EmailSentTrackKind
from lacommunaute.notification.factories import EmailSentTrackFactory
from lacommunaute.notification.models import EmailSentTrack
from lacommunaute.notification.utils import (
    collect_first_replies,
    collect_following_replies,
    collect_new_users_for_onboarding,
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


class CollectFirstRepliesTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.topic = TopicFactory(with_post=True)

    def test_no_reply_to_be_notified(self):
        self.assertEqual(len(list(collect_first_replies())), 0)

    def test_first_reply(self):
        post = PostFactory(topic=self.topic)
        self.assertEqual(
            collect_first_replies(),
            [
                (
                    self.topic.get_absolute_url(with_fqdn=True),
                    self.topic.subject,
                    [self.topic.poster_email],
                    post.poster_display_name,
                )
            ],
        )

    def test_first_reply_since_last_notification(self):
        PostFactory(topic=self.topic)

        EmailSentTrackFactory(kind="dummy")
        self.assertEqual(len(collect_first_replies()), 1)

        EmailSentTrackFactory(kind=EmailSentTrackKind.FIRST_REPLY)
        self.assertEqual(len(collect_first_replies()), 0)


class CollectFollowingRepliesTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.topic = TopicFactory(with_post=True)

    def test_no_reply_to_be_notified(self):
        self.assertEqual(len(list(collect_following_replies())), 0)

    def test_one_reply_to_be_notified(self):
        # first reply
        PostFactory(topic=self.topic, poster__email=self.topic.poster_email)
        EmailSentTrackFactory(kind=EmailSentTrackKind.FOLLOWING_REPLIES)

        # following reply
        PostFactory(topic=self.topic)
        self.assertEqual(
            list(collect_following_replies()),
            [
                (
                    self.topic.get_absolute_url(with_fqdn=True),
                    self.topic.subject,
                    [self.topic.poster_email],
                    "1 nouvelle réponse",
                )
            ],
        )

    def test_multiple_replies_to_be_notified(self):
        PostFactory(topic=self.topic)

        for i in range(2, 10):
            with self.subTest(i=i):
                PostFactory(topic=self.topic)

                self.assertEqual(
                    list(collect_following_replies()),
                    [
                        (
                            self.topic.get_absolute_url(with_fqdn=True),
                            self.topic.subject,
                            sorted(
                                list(
                                    set(
                                        Post.objects.filter(topic=self.topic)
                                        .exclude(id=self.topic.last_post_id)
                                        .values_list("poster__email", flat=True)
                                    )
                                )
                            ),
                            f"{i} nouvelles réponses",
                        )
                    ],
                )

    def test_following_replies_since_last_notification(self):
        PostFactory.create_batch(2, topic=self.topic)

        EmailSentTrackFactory(kind="other")
        self.assertEqual(len(list(collect_following_replies())), 1)

        EmailSentTrackFactory(kind=EmailSentTrackKind.FOLLOWING_REPLIES)
        self.assertEqual(len(list(collect_following_replies())), 0)


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
