from logging import getLogger

from django.core.management.base import BaseCommand

from lacommunaute.notification.models import EmailSentTrack


logger = getLogger("commands")


class Command(BaseCommand):
    help = "Supprimer les anciens enregistrements EmailSentTrack"

    def handle(self, *args, **options):
        nb_deleted = EmailSentTrack.objects.delete_old_records()
        logger.info("%s enregistrements EmailSentTrack supprimés", nb_deleted)
