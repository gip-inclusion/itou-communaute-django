from django.db import models

from lacommunaute.forum.models import Forum
from lacommunaute.stats.enums import Period


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


class ForumStat(models.Model):
    date = models.DateField(verbose_name="Date")
    period = models.CharField(max_length=10, verbose_name="Période", choices=Period.choices)
    forum = models.ForeignKey(Forum, on_delete=models.SET_NULL, verbose_name="Forum", null=True)
    visits = models.IntegerField(verbose_name="Visites", default=0)
    entry_visits = models.IntegerField(verbose_name="Visites entrantes", default=0)
    time_spent = models.IntegerField(verbose_name="Temps passé", default=0)

    objects = models.Manager()

    class Meta:
        verbose_name = "Stat de forum"
        verbose_name_plural = "Stats de forum"
        ordering = ["date", "period", "forum"]
        unique_together = ("date", "period", "forum")

    def __str__(self):
        return f"{self.date} - {self.period} - {self.forum}"
