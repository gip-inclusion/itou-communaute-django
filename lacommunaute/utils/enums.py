from django.db import models


class PeriodAggregation(models.TextChoices):
    MONTH = "MONTH"
    WEEK = "WEEK"
