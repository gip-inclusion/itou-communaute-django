from logging import getLogger

from django.core.management.base import BaseCommand

from lacommunaute.notification.enums import NotificationDelay
from lacommunaute.notification.tasks import send_messages_notifications, send_missyou_notifications


logger = getLogger("commands")


class Command(BaseCommand):
    help = "Envoyer les notifications en file d'attente avec le délai paramétré"

    def add_arguments(self, parser):
        parser.add_argument("delay", type=str, help=f"le délai, un valeur de {str(NotificationDelay.values)}")

    def handle(self, *args, **options):
        try:
            delay = NotificationDelay(options["delay"])
        except ValueError:
            logger.error("le délai fournit doit être un valeuer de %s", str(NotificationDelay.values))

        send_messages_notifications(delay)
        send_missyou_notifications(delay)
        logger.info("That's all, folks!")
