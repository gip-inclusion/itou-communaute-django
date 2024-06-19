from django.core.management.base import BaseCommand

from lacommunaute.surveys.stats import collect_dsp_stats


class Command(BaseCommand):
    help = "Collecter les stats django, jusqu'à la veille de l'execution"

    def handle(self, *args, **options):
        from_date, count = collect_dsp_stats()
        self.stdout.write(self.style.SUCCESS(f"Collecting DSP stats from {from_date} to yesterday: {count} new stats"))
        self.stdout.write(self.style.SUCCESS("That's all, folks!"))
