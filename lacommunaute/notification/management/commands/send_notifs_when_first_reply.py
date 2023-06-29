from django.core.management.base import BaseCommand

from lacommunaute.notification.tasks import send_notifs_when_first_reply


class Command(BaseCommand):
    help = "Envoyer une notification par email à l'auteur d'un sujet quand il y a une première réponse"

    def handle(self, *args, **options):
        send_notifs_when_first_reply()
        self.stdout.write(self.style.SUCCESS("That's all, folks!"))
