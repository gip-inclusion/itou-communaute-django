from django.db import models

from lacommunaute.forum_stats.enums import Period


class Stat(models.Model):
    name = models.CharField(max_length=30, verbose_name="Nom")
    date = models.DateField(verbose_name="Date")
    value = models.IntegerField(verbose_name="Valeur")
    period = models.CharField(max_length=10, verbose_name="Période", choices=Period.choices)

    objects = models.Manager()

    class Meta:
        verbose_name = "Stat"
        verbose_name_plural = "Stats"
        ordering = ["date", "period", "name"]
        unique_together = ("name", "date", "period")

    def __str__(self):
        return f"{self.name} - {self.date} - {self.period}"
