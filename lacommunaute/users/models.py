from django.contrib.auth.models import AbstractUser
from django.db import models

from lacommunaute.users.enums import IdentityProvider


class User(AbstractUser):
    identity_provider = models.CharField(
        max_length=2,
        choices=IdentityProvider.choices,
        null=False,
        blank=False,
    )

    def __str__(self):
        return self.email
