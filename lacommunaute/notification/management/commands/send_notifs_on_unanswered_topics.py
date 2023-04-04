from django.core.management.base import BaseCommand

from lacommunaute.notification.tasks import send_notifs_on_unanswered_topics


class Command(BaseCommand):
    help = "Envoyer une notification par email aux utilisateurs volontaires quand il y a des sujets sans réponse"

    def add_arguments(self, parser):
        parser.add_argument("--list_id", type=int, help="ID de la liste à utiliser")

    def handle(self, *args, **options):
        if "list_id" in options:
            send_notifs_on_unanswered_topics(options["list_id"])
        self.stdout.write(self.style.SUCCESS("That's all, folks!"))
