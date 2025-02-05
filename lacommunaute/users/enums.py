from django.db import models


class IdentityProvider(models.TextChoices):
    INCLUSION_CONNECT = "IC", "Inclusion Connect"
    PRO_CONNECT = "PC", "Pro Connect"
    MAGIC_LINK = "ML", "Magic Link"


class EmailLastSeenKind(models.TextChoices):
    POST = "POST", "message"
    DSP = "DSP", "Diag Parcours IAE"
    EVENT = "EVENT", "évènement public"
    UPVOTE = "UPVOTE", "abonnement"
    FORUM_RATING = "FORUM_RATING", "notation de forum"
    LOGGED = "LOGGED", "connexion"
    VISITED = "VISITED", "notification cliquée"
