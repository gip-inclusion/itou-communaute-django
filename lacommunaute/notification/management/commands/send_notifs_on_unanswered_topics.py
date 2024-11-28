from django.core.management.base import BaseCommand

from lacommunaute.notification.tasks import send_notifs_on_unanswered_topics


class Command(BaseCommand):
    help = "Envoyer une notification par email aux utilisateurs volontaires quand il y a des sujets sans réponse"

    def handle(self, *args, **options):
        send_notifs_on_unanswered_topics()
        self.stdout.write(self.style.SUCCESS("That's all, folks!"))
