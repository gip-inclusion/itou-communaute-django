from logging import getLogger

from django.core.management.base import BaseCommand

from lacommunaute.surveys.stats import collect_dsp_stats


logger = getLogger("commands")


class Command(BaseCommand):
    help = "Collecter les stats django, jusqu'à la veille de l'execution"

    def handle(self, *args, **options):
        from_date, count = collect_dsp_stats()
        logger.info("Collecting DSP stats from %s to yesterday: %s new stats", from_date, count)
        logger.info("That's all, folks!")
