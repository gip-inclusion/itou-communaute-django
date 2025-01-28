import hashlib
import re

import pytest
from django.db import IntegrityError

from lacommunaute.users.enums import EmailLastSeenKind
from lacommunaute.users.factories import EmailLastSeenFactory
from lacommunaute.users.models import EmailLastSeen, User


EMAIL = "alex@honnold.com"


@pytest.fixture(name="email_last_seen")
def fixture_email_last_seen(db):
    return EmailLastSeenFactory(email=EMAIL)


class TestUserModel:
    def test_create_user_without_username(self, db):
        user = User.objects.create_user(email=EMAIL)
        assert re.match(r"^[a-f0-9]{8}(-[a-f0-9]{4}){3}-[a-f0-9]{12}$", user.username)
        assert user.email == EMAIL


class TestEmailLastSeenModel:
    def test_email_uniqueness(self, db, email_last_seen):
        with pytest.raises(IntegrityError):
            EmailLastSeenFactory(email=EMAIL)

    def test_compute_hash_on_save(self, db, email_last_seen):
        assert email_last_seen.email_hash == hashlib.sha256(EMAIL.encode("utf-8")).hexdigest()

    def test_email_hash(self, db):
        email = "janja@garnbret.com"
        hashed_email = "bb247dfe5de638e67be1f4d5414ffbef8d3c93b6dd0513598b013e59640f584b"
        assert hashlib.sha256(email.encode("utf-8")).hexdigest() == hashed_email

    @pytest.mark.parametrize("updated_email", [None, EMAIL])
    def test_hash_remains_unchanged_on_update(self, db, email_last_seen, updated_email):
        email_last_seen.email = updated_email
        email_last_seen.save()
        email_last_seen.refresh_from_db()
        assert email_last_seen.email_hash == hashlib.sha256(EMAIL.encode("utf-8")).hexdigest()

    def test_soft_delete(self, db, email_last_seen):
        email_last_seen.soft_delete()
        email_last_seen.refresh_from_db()
        assert email_last_seen.deleted_at is not None
        assert email_last_seen.email is None
        assert email_last_seen.email_hash not in [None, ""]


class TestEmailLastSeenQueryset:
    @pytest.mark.parametrize("kind", [kind for kind, _ in EmailLastSeenKind.choices])
    def test_seen(self, db, email_last_seen, kind):
        EmailLastSeen.objects.seen(EMAIL, kind)

        email_last_seen.refresh_from_db()
        assert email_last_seen.last_seen_kind == kind
        assert email_last_seen.last_seen_at is not None

    def test_seen_invalid_kind(self, db, email_last_seen):
        with pytest.raises(ValueError):
            EmailLastSeen.objects.seen(EMAIL, "invalid_kind")

    @pytest.mark.parametrize("kind", [kind for kind, _ in EmailLastSeenKind.choices])
    def test_seen_unknown_email(self, db, kind):
        EmailLastSeen.objects.seen(EMAIL, kind)

        email_last_seen = EmailLastSeen.objects.get()
        assert email_last_seen.last_seen_kind == kind
        assert email_last_seen.last_seen_at is not None
