import hashlib
from uuid import uuid4

from django.contrib.auth.models import AbstractUser, UserManager as BaseUserManager
from django.db import models

from lacommunaute.users.enums import EmailLastSeenKind, IdentityProvider


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


class EmailLastSeen(models.Model):
    email = models.EmailField(verbose_name="email", null=True, blank=True, unique=True)
    email_hash = models.CharField(max_length=255, verbose_name="email hash", null=False)
    last_seen_at = models.DateTimeField(verbose_name="last seen at", null=False)
    last_seen_kind = models.CharField(
        max_length=12, verbose_name="last seen kind", choices=EmailLastSeenKind.choices, null=False
    )
    deleted_at = models.DateTimeField(verbose_name="deleted at", null=True, blank=True)

    def __str__(self):
        return f"{self.email} - {self.last_seen_at}"

    def save(self, *args, **kwargs):
        if self.email:
            self.email_hash = hashlib.sha256(self.email.encode("utf-8")).hexdigest()
        super().save(*args, **kwargs)
