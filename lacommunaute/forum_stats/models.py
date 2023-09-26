from django.db import models

from lacommunaute.forum_stats.enums import Period


class StatQuerySet(models.QuerySet):
    def current_month_datas(self):
        qs = Stat.objects.filter(period="month").order_by("-date")

        if qs.exists():
            return Stat.objects.filter(date=qs.first().date, period=Period.MONTH).values("name", "value", "date")

        return Stat.objects.none()


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

    objects = StatQuerySet().as_manager()
