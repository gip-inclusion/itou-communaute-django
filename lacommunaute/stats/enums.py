from django.db import models


class Period(models.TextChoices):
    MONTH = "month"
    WEEK = "week"
    DAY = "day"
