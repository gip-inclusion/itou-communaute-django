# test EmailSentTrack model
from django.test import TestCase

from lacommunaute.notification.models import EmailSentTrack


class EmailSentTrackModelTest(TestCase):
    def test_str(self):
        track = EmailSentTrack(status_code=200)
        self.assertEqual(str(track), f"200 - {track.created}")
