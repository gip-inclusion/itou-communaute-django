from django.conf import settings
from django.db import models
from machina.models.abstract_models import DatedModel


class Event(DatedModel):
    name = models.CharField(max_length=100, verbose_name="Nom")
    date = models.DateField(verbose_name="Date de début", help_text="au format JJ/MM/YYYY")
    time = models.TimeField(verbose_name="Heure de début", help_text="au format HH:MM")
    end_date = models.DateField(verbose_name="Date de fin", help_text="au format JJ/MM/YYYY")
    end_time = models.TimeField(verbose_name="Heure de fin", help_text="au format HH:MM")
    color = models.IntegerField(verbose_name="Color", default=1)
    description = models.TextField(verbose_name="Notes", blank=True, null=True)

    location = models.URLField(verbose_name="Lien vers l'évènement", null=True, blank=True)
    poster = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name="Poster",
    )

    objects = models.Manager()

    class Meta:
        verbose_name = "Event"
        verbose_name_plural = "Events"
        ordering = ["-date", "-time"]

    def __str__(self):
        return f"{self.name} - {self.date}"
