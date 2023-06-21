from django.core.management.base import BaseCommand

from lacommunaute.notification.tasks import send_notifs_on_following_replies


class Command(BaseCommand):
    help = "Envoyer une notification par email à l'auteur d'un sujet quand il y a de nouvelles réponses"

    def handle(self, *args, **options):
        send_notifs_on_following_replies()
        self.stdout.write(self.style.SUCCESS("That's all, folks!"))
