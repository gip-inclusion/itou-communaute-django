from django.conf import settings
from django.test import TestCase

from lacommunaute.forum_conversation.factories import PostFactory, TopicFactory
from lacommunaute.notification.factories import EmailSentTrackFactory
from lacommunaute.notification.models import EmailSentTrack
from lacommunaute.notification.utils import collect_first_replies, last_notification


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
        EmailSentTrackFactory()

        self.assertEqual(len(collect_first_replies()), 0)

    def test_replies_since_last_notification(self):
        EmailSentTrackFactory()
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
