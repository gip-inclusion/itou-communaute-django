import hashlib

import pytest
from django.conf import settings

from lacommunaute.forum_conversation.factories import AnonymousTopicFactory, TopicFactory
from lacommunaute.users.factories import EmailLastSeenFactory, UserFactory
from lacommunaute.users.models import EmailLastSeen
from lacommunaute.users.utils import soft_delete_users


@pytest.fixture(name="soft_deletable_email_last_seen")
def fixture_soft_deletable_email_last_seen(db):
    return


def test_soft_delete(db):
    email_last_seen = EmailLastSeenFactory(soft_deletable=True)
    expected_hash = hashlib.sha256(
        f"{email_last_seen.email}-{settings.EMAIL_LAST_SEEN_HASH_SALT}".encode("utf-8")
    ).hexdigest()

    soft_delete_users([email_last_seen])

    email_last_seen.refresh_from_db()
    assert email_last_seen.deleted_at is not None
    assert email_last_seen.email == f"email-anonymise-{email_last_seen.pk}@{settings.COMMU_FQDN}"
    assert email_last_seen.email_hash == expected_hash


def test_soft_delete_user(db):
    user = UserFactory()
    email_last_seen = EmailLastSeenFactory(email=user.email, soft_deletable=True)

    undesired_user = UserFactory()
    undesired_user_email = undesired_user.email
    undesired_user_first_name = undesired_user.first_name
    undesired_user_last_name = undesired_user.last_name

    soft_delete_users([email_last_seen])

    user.refresh_from_db()
    assert user.email == f"email-anonymise-{email_last_seen.pk}@{settings.COMMU_FQDN}"
    assert user.first_name == "Anonyme"
    assert user.last_name == "Anonyme"

    undesired_user.refresh_from_db()
    assert undesired_user.email == undesired_user_email
    assert undesired_user.first_name == undesired_user_first_name
    assert undesired_user.last_name == undesired_user_last_name


def test_soft_delete_post(db):
    anonymous_post = AnonymousTopicFactory(with_post=True).first_post
    email_last_seen = EmailLastSeen.objects.get()

    undesired_posts = [AnonymousTopicFactory(with_post=True).first_post, TopicFactory(with_post=True).first_post]
    undesired_usernames = [post.username for post in undesired_posts]

    soft_delete_users([email_last_seen])

    anonymous_post.refresh_from_db()
    assert anonymous_post.username == f"email-anonymise-{email_last_seen.pk}@{settings.COMMU_FQDN}"

    for post in undesired_posts:
        post.refresh_from_db()
        assert post.username in undesired_usernames


def test_soft_delete_numqueries(db, django_assert_num_queries):
    AnonymousTopicFactory.create_batch(3, with_post=True)

    users = UserFactory.create_batch(3)
    for user in users:
        EmailLastSeenFactory(email=user.email, soft_deletable=True)

    with django_assert_num_queries(
        2  # savepoint, release
        + 2  # select/update email last seen
        + 2  # select/update user
        + 2  # select/update post
    ):
        soft_delete_users(EmailLastSeen.objects.all())
