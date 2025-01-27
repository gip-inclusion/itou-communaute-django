import hashlib
import re

import pytest
from django.db import IntegrityError

from lacommunaute.users.enums import EmailLastSeenKind
from lacommunaute.users.factories import EmailLastSeenFactory
from lacommunaute.users.models import EmailLastSeen, User


email = "alex@honnold.com"


@pytest.fixture(name="email_last_seen")
def fixture_email_last_seen(db):
    return EmailLastSeenFactory(email=email)


# User model tests


def test_create_user_without_username(db):
    user = User.objects.create_user(email=email)
    assert re.match(r"^[a-f0-9]{8}(-[a-f0-9]{4}){3}-[a-f0-9]{12}$", user.username)
    assert user.email == email


# EmailLastSeen model tests


def test_email_uniqueness(db, email_last_seen):
    with pytest.raises(IntegrityError):
        EmailLastSeenFactory(email=email)


def test_compute_hash_on_save(db, email_last_seen):
    assert email_last_seen.email_hash == hashlib.sha256(email.encode("utf-8")).hexdigest()


@pytest.mark.parametrize("updated_email", [None, email])
def test_hash_remains_unchanged_on_update(db, email_last_seen, updated_email):
    email_last_seen.email = updated_email
    email_last_seen.save()
    email_last_seen.refresh_from_db()
    assert email_last_seen.email_hash == hashlib.sha256(email.encode("utf-8")).hexdigest()


def test_soft_delete(db, email_last_seen):
    email_last_seen.soft_delete()
    email_last_seen.refresh_from_db()
    assert email_last_seen.deleted_at is not None
    assert email_last_seen.email is None
    assert email_last_seen.email_hash not in [None, ""]


# EmailLastSeenQuerySet tests


@pytest.mark.parametrize("kind", [kind for kind, _ in EmailLastSeenKind.choices])
def test_seen(db, email_last_seen, kind):
    EmailLastSeen.objects.seen(email, kind)

    email_last_seen.refresh_from_db()
    assert email_last_seen.last_seen_kind == kind
    assert email_last_seen.last_seen_at is not None


def test_seen_invalid_kind(db, email_last_seen):
    with pytest.raises(ValueError):
        EmailLastSeen.objects.seen(email, "invalid_kind")


@pytest.mark.parametrize("kind", [kind for kind, _ in EmailLastSeenKind.choices])
def test_seen_unknown_email(db, kind):
    EmailLastSeen.objects.seen(email, kind)

    email_last_seen = EmailLastSeen.objects.get(email=email)
    assert email_last_seen.last_seen_kind == kind
    assert email_last_seen.last_seen_at is not None
