from logging import getLogger

from django.core.management.base import BaseCommand

from lacommunaute.notification.tasks import send_notifs_on_unanswered_topics


logger = getLogger("commands")


class Command(BaseCommand):
    help = "Envoyer une notification par email aux utilisateurs volontaires quand il y a des sujets sans réponse"

    def handle(self, *args, **options):
        send_notifs_on_unanswered_topics()
        logger.info("That's all, folks!")
