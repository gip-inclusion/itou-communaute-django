from django.contrib.auth.models import AnonymousUser
from django.db.models import F
from django.test import TestCase

from lacommunaute.forum_conversation.factories import TopicFactory
from lacommunaute.notification.enums import EmailSentTrackKind
from lacommunaute.notification.factories import NotificationFactory
from lacommunaute.notification.models import EmailSentTrack, Notification
from lacommunaute.users.factories import UserFactory


class EmailSentTrackModelTest(TestCase):
    def test_str(self):
        track = EmailSentTrack(status_code=200)
        self.assertEqual(str(track), f"200 - {track.created}")


class NotificationQuerySetTest(TestCase):
    def test_notification_group_by_recipient(self):
        self.assertEqual(Notification.objects.all().group_by_recipient(), {})

        recipient_a = "test@example.com"
        NotificationFactory(recipient=recipient_a, kind=EmailSentTrackKind.FIRST_REPLY)
        NotificationFactory(recipient=recipient_a, kind=EmailSentTrackKind.FOLLOWING_REPLIES)
        NotificationFactory(recipient=recipient_a, kind=EmailSentTrackKind.FIRST_REPLY)

        recipient_b = "test2@example.com"
        notification_b = NotificationFactory(recipient=recipient_b)

        result = Notification.objects.all().group_by_recipient()
        self.assertEqual(len(result.keys()), 2)

        self.assertEqual(
            result[recipient_a], list(Notification.objects.filter(recipient=recipient_a).order_by("kind"))
        )

        self.assertEqual(result[recipient_b], [notification_b])

    def test_mark_topic_posts_read(self):
        user = UserFactory()
        topic = TopicFactory(with_post=True)

        NotificationFactory.create_batch(2, recipient=user.email, post=topic.first_post)

        Notification.objects.mark_topic_posts_read(topic, user)

        self.assertEqual(
            Notification.objects.filter(
                sent_at__isnull=False, post=topic.first_post, recipient=user.email, sent_at=F("created")
            ).count(),
            2,
        )

    def test_mark_topic_posts_read_doesnt_impact_old_notifications(self):
        user = UserFactory()
        topic = TopicFactory(with_post=True)

        old_notification = NotificationFactory(recipient=user.email, post=topic.first_post, is_sent=True)
        self.assertNotEqual(str(old_notification.sent_at), str(old_notification.created))

        Notification.objects.mark_topic_posts_read(topic, user)

        old_notification.refresh_from_db()
        self.assertNotEqual(str(old_notification.sent_at), str(old_notification.created))

    def test_mark_topic_posts_read_doesnt_impact_other_notifications(self):
        user = UserFactory()
        topic = TopicFactory(with_post=True)

        other_notification = NotificationFactory(recipient="test@example.com", post=topic.first_post)

        Notification.objects.mark_topic_posts_read(topic, user)

        other_notification.refresh_from_db()
        self.assertIsNone(other_notification.sent_at)

    def test_mark_topic_posts_read_anonymous_user(self):
        topic = TopicFactory(with_post=True)

        with self.assertRaises(ValueError):
            Notification.objects.mark_topic_posts_read(topic, AnonymousUser())

    def test_mark_topic_posts_read_invalid_arguments(self):
        user = UserFactory()
        topic = TopicFactory(with_post=True)

        with self.assertRaises(ValueError):
            Notification.objects.mark_topic_posts_read(None, user)

        with self.assertRaises(ValueError):
            Notification.objects.mark_topic_posts_read(topic, None)
