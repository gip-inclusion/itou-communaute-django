from django.db import models


class Filters(models.TextChoices):
    ALL = "ALL", "les plus récentes"
    NEW = "NEW", "en attente de réponse"
