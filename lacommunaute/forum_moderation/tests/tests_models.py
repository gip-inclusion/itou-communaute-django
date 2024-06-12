import pytest
from django.db import IntegrityError

from lacommunaute.forum_conversation.models import Post
from lacommunaute.forum_moderation.enums import BlockedPostReason
from lacommunaute.forum_moderation.factories import BlockedDomainNameFactory, BlockedEmailFactory
from lacommunaute.forum_moderation.models import BlockedPost


def test_blocked_email_uniqueness(db):
    blocked = BlockedEmailFactory()
    with pytest.raises(IntegrityError):
        BlockedEmailFactory(email=blocked.email)


def test_blocked_domain_name_uniqueness(db):
    blocked = BlockedDomainNameFactory()
    with pytest.raises(IntegrityError):
        BlockedDomainNameFactory(domain=blocked.domain)


def test_blocked_post_create_from_post(db):
    post = Post(update_reason=BlockedPostReason.ALTERNATIVE_LANGUAGE.label)
    blocked_post = BlockedPost.create_from_post(post)
    assert blocked_post.block_reason == BlockedPostReason.ALTERNATIVE_LANGUAGE

    with pytest.raises(TypeError):
        BlockedPost.create_from_post(post, "String reason")

    post = Post(update_reason="A non existant reason")
    with pytest.raises(ValueError):
        BlockedPost.create_from_post(post)

    post = Post(update_reason=None)
    with pytest.raises(ValueError):
        BlockedPost.create_from_post(post)
