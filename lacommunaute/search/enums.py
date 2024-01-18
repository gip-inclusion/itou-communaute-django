from django.db import models


class CommonIndexKind(models.TextChoices):
    TOPIC = "TOPIC", "topic"
    FORUM = "FORUM", "forum"
