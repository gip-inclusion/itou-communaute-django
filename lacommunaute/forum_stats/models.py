from django.db import models
from django.utils.translation import gettext_lazy as _

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


class SearchCollectionPeriod(models.Model):
    name = models.CharField(max_length=256, verbose_name=_("Name"))
    start_date = models.DateField(verbose_name=_("Start date"), help_text=_("The start of the period"))
    end_date = models.DateField(verbose_name=_("End date"), help_text=_("The end of the period"))

    class Meta:
        verbose_name = _("Search Collection Period")
        verbose_name_plural = _("Search Collection Periods")
        ordering = ["-end_date", "-start_date"]
        unique_together = ("start_date", "end_date")

    def __str__(self):
        return f"Period {str(self.name)} ({str(self.start_date)} - {str(self.end_date)})"


class SearchQuery(models.Model):
    """
    Matomo logs for us the searches made by users visiting the site.
    We collect searches made during a period and store them for interpretation
    """

    label = models.TextField(help_text=_("The search query made by the user"))
    period = models.ForeignKey(
        SearchCollectionPeriod, related_name="searches", on_delete=models.CASCADE, db_index=True
    )
    nb_visits = models.PositiveIntegerField(verbose_name=_("Number visits"))

    class Meta:
        verbose_name = _("Search Query")
        verbose_name_plural = _("Search Queries")
        ordering = ["-period", "label"]

    def __str__(self):
        return f"Search from {str(self.period)}"
