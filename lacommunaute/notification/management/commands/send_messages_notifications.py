from django.core.management.base import BaseCommand

from lacommunaute.notification.enums import NotificationDelay
from lacommunaute.notification.tasks import send_messages_notifications


class Command(BaseCommand):
    help = "Envoyer les notifications en file d'attente avec le délai paramétré"

    def add_arguments(self, parser):
        parser.add_argument("delay", type=str, help=f"le délai, un valeur de {str(NotificationDelay.values)}")

    def handle(self, *args, **options):
        try:
            delay = NotificationDelay(options["delay"])
        except ValueError:
            self.stdout.write(
                self.style.ERROR(f"le délai fournit doit être un valeuer de {str(NotificationDelay.values)}")
            )

        send_messages_notifications(delay)
        self.stdout.write(self.style.SUCCESS("That's all, folks!"))
