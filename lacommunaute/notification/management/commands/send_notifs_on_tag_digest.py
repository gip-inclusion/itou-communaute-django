from django.core.management.base import BaseCommand

from lacommunaute.notification.tasks import send_notifs_on_tag_digest


class Command(BaseCommand):
    help = "Envoyer un digest des topics aux utilisateurs qui ont souscrit à un tag"

    def handle(self, *args, **options):
        send_notifs_on_tag_digest()
        self.stdout.write(self.style.SUCCESS("That's all, folks!"))
