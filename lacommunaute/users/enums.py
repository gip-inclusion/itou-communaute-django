from django.db import models


class IdentityProvider(models.TextChoices):
    INCLUSION_CONNECT = "IC", "Inclusion Connect"
    PRO_CONNECT = "PC", "ProConnect"
    MAGIC_LINK = "ML", "Magic Link"


class EmailLastSeenKind(models.TextChoices):
    POST = "POST", "message"
    LOGGED = "LOGGED", "connexion"
    VISITED = "VISITED", "notification cliquée"
