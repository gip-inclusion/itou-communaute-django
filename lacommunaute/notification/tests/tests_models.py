from django.db import IntegrityError
from django.test import TestCase

from lacommunaute.notification.factories import BouncedDomainNameFactory, BouncedEmailFactory
from lacommunaute.notification.models import EmailSentTrack


class EmailSentTrackModelTest(TestCase):
    def test_str(self):
        track = EmailSentTrack(status_code=200)
        self.assertEqual(str(track), f"200 - {track.created}")


class BouncedEmailModelTest(TestCase):
    def test_uniqueness(self):
        bounced = BouncedEmailFactory()
        with self.assertRaises(IntegrityError):
            BouncedEmailFactory(email=bounced.email)


class BouncedDomainNameModelTest(TestCase):
    def test_uniqueness(self):
        bounced = BouncedDomainNameFactory()
        with self.assertRaises(IntegrityError):
            BouncedDomainNameFactory(domain=bounced.domain)
