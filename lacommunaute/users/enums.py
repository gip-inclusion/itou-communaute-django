from django.db import models


class IdentityProvider(models.TextChoices):
    INCLUSION_CONNECT = "IC", "Inclusion Connect"
    PRO_CONNECT = "PC", "Pro Connect"
