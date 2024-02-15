from django.db import models


class EmailSentTrackKind(models.TextChoices):
    FIRST_REPLY = "first_reply", "Première réponse à un sujet"
    FOLLOWING_REPLIES = "following_replies", "Réponses suivantes"
    ONBOARDING = "onboarding", "Onboarding d'un nouvel utilisateur"
    PENDING_TOPIC = "pending_topic", "Question sans réponse"
    TAG_DIGEST = "tag_digest", "Résumé de tags"
