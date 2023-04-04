from django.db import models


class EmailSentTrackKind(models.TextChoices):
    FIRST_REPLY = "first_reply", "Première réponse à un sujet"
    ONBOARDING = "onboarding", "Onboarding d'un nouvel utilisateur"
    PENDING_TOPIC = "pending_topic", "Question sans réponse"
