from logging import getLogger

from django.conf import settings
from django.core.management.base import BaseCommand

from lacommunaute.notification.enums import EmailSentTrackKind, NotificationDelay
from lacommunaute.notification.models import Notification
from lacommunaute.users.models import EmailLastSeen


logger = getLogger("commands")


class Command(BaseCommand):
    help = "collecte des plus anciens emails non vus"

    def handle(self, *args, **options):
        logger.info("starting to get emails from EmailLastSeen table")

        email_last_seens = EmailLastSeen.objects.eligible_to_missyou_message()[
            : settings.EMAIL_LAST_SEEN_MISSYOU_BATCH_SIZE
        ]

        notifications = [
            Notification(
                recipient=email_last_seen.email,
                kind=EmailSentTrackKind.MISSYOU,
                delay=NotificationDelay.ASAP,
            )
            for email_last_seen in email_last_seens
        ]

        Notification.objects.bulk_create(notifications)

        logger.info("%s emails collected", len(notifications))
