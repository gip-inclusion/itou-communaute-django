import hashlib
import re

import pytest
from dateutil.relativedelta import relativedelta
from django.conf import settings
from django.db import IntegrityError
from django.utils import timezone

from lacommunaute.users.enums import EmailLastSeenKind
from lacommunaute.users.factories import EmailLastSeenFactory
from lacommunaute.users.models import EmailLastSeen, User


EMAIL = "alex@honnold.com"


@pytest.fixture(name="email_last_seen")
def fixture_email_last_seen(db):
    return EmailLastSeenFactory(email=EMAIL)


def test_email_hash(db):
    expected_hash = "a988454cba6b19df0360d1d00ebfc89b2b73dd760fb7aab95dcf2992bbf82a7e"
    computed_hash = hashlib.sha256(f"{EMAIL}-{settings.EMAIL_LAST_SEEN_HASH_SALT}".encode("utf-8")).hexdigest()
    assert expected_hash == computed_hash


class TestUserModel:
    def test_create_user_without_username(self, db):
        user = User.objects.create_user(email=EMAIL)
        assert re.match(r"^[a-f0-9]{8}(-[a-f0-9]{4}){3}-[a-f0-9]{12}$", user.username)
        assert user.email == EMAIL


class TestEmailLastSeenModel:
    def test_email_uniqueness(self, db, email_last_seen):
        with pytest.raises(IntegrityError):
            EmailLastSeenFactory(email=EMAIL)

    def test_email_is_not_null(self, db):
        with pytest.raises(IntegrityError):
            EmailLastSeenFactory(email=None)


class TestEmailLastSeenQueryset:
    @pytest.mark.parametrize("kind", [kind for kind, _ in EmailLastSeenKind.choices])
    def test_seen(self, db, email_last_seen, kind):
        EmailLastSeen.objects.seen(EMAIL, kind)

        email_last_seen.refresh_from_db()
        assert email_last_seen.last_seen_kind == kind
        assert email_last_seen.last_seen_at is not None
        assert email_last_seen.missyou_send_at is None

    def test_seen_invalid_kind(self, db, email_last_seen):
        with pytest.raises(ValueError):
            EmailLastSeen.objects.seen(EMAIL, "invalid_kind")

    @pytest.mark.parametrize("kind", [kind for kind, _ in EmailLastSeenKind.choices])
    def test_seen_unknown_email(self, db, kind):
        EmailLastSeen.objects.seen(EMAIL, kind)

        email_last_seen = EmailLastSeen.objects.get()
        assert email_last_seen.last_seen_kind == kind
        assert email_last_seen.last_seen_at is not None

    @pytest.mark.parametrize("email_last_seen", [None, lambda: EmailLastSeenFactory()])
    def test_numqueries(self, db, django_assert_num_queries, email_last_seen):
        if email_last_seen:
            email_last_seen = email_last_seen()

        email = email_last_seen.email if email_last_seen else EMAIL
        kind = email_last_seen.last_seen_kind if email_last_seen else EmailLastSeenKind.POST

        with django_assert_num_queries(1):
            EmailLastSeen.objects.seen(email=email, kind=kind)

    def test_missyou_send_at_is_reset(self, db):
        email_last_seen = EmailLastSeenFactory(missyou_send_at=timezone.now())
        EmailLastSeen.objects.seen(email_last_seen.email, EmailLastSeenKind.POST)

        email_last_seen.refresh_from_db()
        assert email_last_seen.missyou_send_at is None

    def test_eligible_to_missyou_message(self, db):
        expected = EmailLastSeenFactory(
            last_seen_at=timezone.now() - relativedelta(days=settings.EMAIL_LAST_SEEN_MISSYOU_DELAY),
        )
        # undesired
        EmailLastSeenFactory(
            last_seen_at=timezone.now() - relativedelta(days=(settings.EMAIL_LAST_SEEN_MISSYOU_DELAY - 1))
        )
        EmailLastSeenFactory(
            last_seen_at=timezone.now() - relativedelta(days=settings.EMAIL_LAST_SEEN_MISSYOU_DELAY),
            missyou_sent=True,
        )

        email_last_seen = EmailLastSeen.objects.eligible_to_missyou_message().get()
        assert email_last_seen == expected

    def test_eligible_to_missyou_message_order(self, db):
        for i in range(3):
            EmailLastSeenFactory(
                last_seen_at=timezone.now() - relativedelta(days=(settings.EMAIL_LAST_SEEN_MISSYOU_DELAY + i))
            )
        qs = EmailLastSeen.objects.eligible_to_missyou_message()
        assert qs.count() == 3
        assert list(qs) == list(qs.order_by("last_seen_at"))

    def test_eligible_to_soft_deletion(self, db):
        expected = EmailLastSeenFactory(soft_deletable=True)
        # undesired
        EmailLastSeenFactory(soft_deleted=True)
        EmailLastSeenFactory(
            missyou_send_at=timezone.now()
            - relativedelta(days=settings.EMAIL_LAST_SEEN_ARCHIVE_PERSONNAL_DATAS_DELAY - 1)
        )

        email_last_seen = EmailLastSeen.objects.eligible_to_soft_deletion().get()
        assert email_last_seen == expected
