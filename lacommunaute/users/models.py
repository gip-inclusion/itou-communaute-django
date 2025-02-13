import hashlib
from uuid import uuid4

from dateutil.relativedelta import relativedelta
from django.conf import settings
from django.contrib.auth.models import AbstractUser, UserManager as BaseUserManager
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

        return EmailLastSeen.objects.bulk_create(
            [EmailLastSeen(email=email, last_seen_at=timezone.now(), last_seen_kind=kind, missyou_send_at=None)],
            update_fields=["last_seen_at", "last_seen_kind", "missyou_send_at"],
            update_conflicts=True,
            unique_fields=["email"],
        )

    def eligible_to_missyou_message(self):
        return self.filter(
            last_seen_at__lte=timezone.now() - relativedelta(months=settings.EMAIL_LAST_SEEN_MISSYOU_DELAY),
            missyou_send_at=None,
        ).order_by("last_seen_at")

    def eligible_to_soft_deletion(self):
        return self.filter(
            missyou_send_at__lte=timezone.now()
            - relativedelta(days=settings.EMAIL_LAST_SEEN_ARCHIVE_PERSONNAL_DATAS_DELAY),
            deleted_at=None,
        )


class EmailLastSeen(models.Model):
    email = models.EmailField(verbose_name="email", null=False, unique=True)
    email_hash = models.CharField(max_length=255, verbose_name="email hash", null=True)
    last_seen_at = models.DateTimeField(verbose_name="last seen at", null=False)
    last_seen_kind = models.CharField(
        max_length=12, verbose_name="last seen kind", choices=EmailLastSeenKind.choices, null=False
    )
    missyou_send_at = models.DateTimeField(verbose_name="miss you sent at", null=True, blank=True)
    deleted_at = models.DateTimeField(verbose_name="deleted at", null=True, blank=True)

    objects = EmailLastSeenQuerySet.as_manager()

    def soft_delete(self):
        self.deleted_at = timezone.now()
        salted_email = f"{self.email}-{settings.EMAIL_LAST_SEEN_HASH_SALT}"
        self.email_hash = hashlib.sha256(salted_email.encode("utf-8")).hexdigest()
        self.email = f"email-anonymisé-{self.pk}"
        self.save()
