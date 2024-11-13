from django.db import models
from django.utils.translation import gettext_lazy as _


class EmailSentTrackKind(models.TextChoices):
    FIRST_REPLY = "first_reply", "Première réponse à un sujet"
    FOLLOWING_REPLIES = "following_replies", "Réponses suivantes"
    ONBOARDING = "onboarding", "Onboarding d'un nouvel utilisateur"
    PENDING_TOPIC = "pending_topic", "Question sans réponse"
    MAGIC_LINK = "magic_link", "Lien de connexion magique"


class NotificationDelay(models.TextChoices):
    ASAP = "asap", _("As soon as possible")
    DAY = "day", _("The following day")
