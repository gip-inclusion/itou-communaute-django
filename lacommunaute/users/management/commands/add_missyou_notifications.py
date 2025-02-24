from logging import getLogger

from django.conf import settings
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from lacommunaute.notification.enums import EmailSentTrackKind, NotificationDelay
from lacommunaute.notification.models import Notification
from lacommunaute.users.models import EmailLastSeen


logger = getLogger("commands")


class Command(BaseCommand):
    help = "collecte des plus anciens emails non vus"

    @transaction.atomic
    def handle(self, *args, **options):
        logger.info("starting to get emails from EmailLastSeen table")

        notifications = []

        for email_last_seen in (
            email_last_seens := EmailLastSeen.objects.eligible_to_missyou_message()[
                : settings.EMAIL_LAST_SEEN_MISSYOU_BATCH_SIZE
            ]
        ):
            notifications += [
                Notification(
                    recipient=email_last_seen.email,
                    kind=EmailSentTrackKind.MISSYOU,
                    delay=NotificationDelay.ASAP,
                )
            ]

            email_last_seen.missyou_send_at = timezone.now()

        Notification.objects.bulk_create(notifications)
        EmailLastSeen.objects.bulk_update(email_last_seens, ["missyou_send_at"])

        logger.info("%s emails collected", len(notifications))
