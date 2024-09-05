from django.db import models


class Kind(models.TextChoices):
    PUBLIC_FORUM = "PUBLIC_FORUM", "Espace public"
    NEWS = "NEWS", "Actualités"
