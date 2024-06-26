from django.db import models
from django.utils.translation import gettext_lazy as _


class EmailSentTrackKind(models.TextChoices):
    FIRST_REPLY = "first_reply", "Première réponse à un sujet"
    FOLLOWING_REPLIES = "following_replies", "Réponses suivantes"
    ONBOARDING = "onboarding", "Onboarding d'un nouvel utilisateur"
    PENDING_TOPIC = "pending_topic", "Question sans réponse"
    NEW_MESSAGES = "new_messages", _("New messages")


class NotificationDelay(models.TextChoices):
    ASAP = "asap", _("As soon as possible")
    DAY = "day", _("The following day")
