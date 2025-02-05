import hashlib
import re

import pytest
from django.conf import settings
from django.db import IntegrityError

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

    def test_email_is_not_null(self, db):
        with pytest.raises(IntegrityError):
            EmailLastSeenFactory(email=None)

    def test_email_hash(self, db):
        expected_hash = "a988454cba6b19df0360d1d00ebfc89b2b73dd760fb7aab95dcf2992bbf82a7e"
        computed_hash = hashlib.sha256(f"{EMAIL}-{settings.EMAIL_LAST_SEEN_HASH_SALT}".encode("utf-8")).hexdigest()
        assert expected_hash == computed_hash

    def test_soft_delete(self, db, email_last_seen):
        expected_hash = hashlib.sha256(f"{EMAIL}-{settings.EMAIL_LAST_SEEN_HASH_SALT}".encode("utf-8")).hexdigest()
        email_last_seen.soft_delete()
        email_last_seen.refresh_from_db()
        assert email_last_seen.deleted_at is not None
        assert email_last_seen.email == f"email-anonymisé-{email_last_seen.pk}"
        assert email_last_seen.email_hash == expected_hash
