from uuid import uuid4

from django.contrib.auth.models import AbstractUser, UserManager as BaseUserManager
from django.db import models

from lacommunaute.users.enums import IdentityProvider


class UserManager(BaseUserManager):
    def create_user(self, username=None, email=None, password=None, **extra_fields):
        if not username:
            username = str(uuid4())
        return super().create_user(username, email, password, **extra_fields)


class User(AbstractUser):
    identity_provider = models.CharField(
        max_length=2,
        choices=IdentityProvider.choices,
        null=False,
        blank=False,
    )

    objects = UserManager()

    def __str__(self):
        return self.email
