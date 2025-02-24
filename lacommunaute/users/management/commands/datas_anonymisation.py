from logging import getLogger

from django.core.management.base import BaseCommand

from lacommunaute.users.models import EmailLastSeen
from lacommunaute.users.utils import soft_delete_users


logger = getLogger("commands")


class Command(BaseCommand):
    help = "anonymisation des données personnelles, X jours après la notification"

    def handle(self, *args, **options):
        logger.info("starting to soft delete users from EmailLastSeen table")
        qs = EmailLastSeen.objects.eligible_to_soft_deletion()
        user_count, post_count, email_last_seen_count = soft_delete_users(qs)
        logger.info(
            "%s users anonymised, %s posts anonymised, %s email_last_seen anonymised",
            user_count,
            post_count,
            email_last_seen_count,
        )
