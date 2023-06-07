from django.db import models


class Filters(models.TextChoices):
    ALL = "ALL", "Les plus récentes"
    NEW = "NEW", "En attente de réponse"
    CERTIFIED = "CERTIFIED", "Réponse certifiée"
