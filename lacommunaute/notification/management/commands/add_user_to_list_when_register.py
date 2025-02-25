from logging import getLogger

from django.core.management.base import BaseCommand

from lacommunaute.notification.tasks import add_user_to_list_when_register


logger = getLogger("commands")


class Command(BaseCommand):
    help = "Ajouter un utilisateur à une liste Sendinblue quand il s'inscrit"

    def handle(self, *args, **options):
        add_user_to_list_when_register()
        logger.info("That's all, folks!")
