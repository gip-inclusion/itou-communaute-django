from django.test import TestCase

from lacommunaute.notification.enums import EmailSentTrackKind
from lacommunaute.notification.factories import NotificationFactory
from lacommunaute.notification.models import EmailSentTrack, Notification


class EmailSentTrackModelTest(TestCase):
    def test_str(self):
        track = EmailSentTrack(status_code=200)
        self.assertEqual(str(track), f"200 - {track.created}")

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
