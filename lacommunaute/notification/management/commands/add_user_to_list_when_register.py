from django.core.management.base import BaseCommand

from lacommunaute.notification.tasks import add_user_to_list_when_register


class Command(BaseCommand):
    help = "Ajouter un utilisateur à une liste Sendinblue quand il s'inscrit"

    def handle(self, *args, **options):

        add_user_to_list_when_register()
        self.stdout.write(self.style.SUCCESS("That's all, folks!"))
