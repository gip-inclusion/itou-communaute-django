import hashlib
from uuid import uuid4

from django.contrib.auth.models import AbstractUser, UserManager as BaseUserManager
from django.contrib.auth.signals import user_logged_in
from django.db import models
from django.utils import timezone

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


class EmailLastSeenQuerySet(models.QuerySet):
    def seen(self, email, kind):
        if kind not in [kind for kind, _ in EmailLastSeenKind.choices]:
            raise ValueError(f"Invalid kind: {kind}")

        return self.update_or_create(email=email, defaults={"last_seen_at": timezone.now(), "last_seen_kind": kind})


class EmailLastSeen(models.Model):
    email = models.EmailField(verbose_name="email", null=True, blank=True, unique=True)
    email_hash = models.CharField(max_length=255, verbose_name="email hash", null=False)
    last_seen_at = models.DateTimeField(verbose_name="last seen at", null=False)
    last_seen_kind = models.CharField(
        max_length=12, verbose_name="last seen kind", choices=EmailLastSeenKind.choices, null=False
    )
    deleted_at = models.DateTimeField(verbose_name="deleted at", null=True, blank=True)

    objects = EmailLastSeenQuerySet.as_manager()

    def __str__(self):
        return f"{self.email} - {self.last_seen_at}"

    def save(self, *args, **kwargs):
        if self.email:
            self.email_hash = hashlib.sha256(self.email.encode("utf-8")).hexdigest()
        super().save(*args, **kwargs)

    def soft_delete(self):
        self.deleted_at = timezone.now()
        self.email = None
        self.save()


def update_email_last_seen(sender, user, request, **kwargs):
    EmailLastSeen.objects.seen(email=user.email, kind=EmailLastSeenKind.LOGGED)


user_logged_in.connect(update_email_last_seen, dispatch_uid="update_email_last_seen")
