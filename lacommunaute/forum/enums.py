from django.db import models


class Kind(models.TextChoices):
    PUBLIC_FORUM = "PUBLIC_FORUM", "Espace public"
    PRIVATE_FORUM = "PRIVATE_FORUM", "Espace privé"
    NEWS = "NEWS", "Actualités"
