from dateutil.relativedelta import relativedelta
from django.core.management import call_command
from django.utils import timezone

from lacommunaute.notification.factories import EmailSentTrackFactory
from lacommunaute.notification.models import EmailSentTrack


def test_delete_old_email_sent_tracks(db):
    EmailSentTrackFactory(created=timezone.now() - relativedelta(days=90))
    call_command("delete_old_email_sent_tracks")
    assert EmailSentTrack.objects.count() == 0
