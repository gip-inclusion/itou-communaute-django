import pytest
from django.db import IntegrityError

from lacommunaute.forum_moderation.factories import BlockedDomainNameFactory, BlockedEmailFactory


def test_blocked_email_uniqueness(db):
    blocked = BlockedEmailFactory()
    with pytest.raises(IntegrityError):
        BlockedEmailFactory(email=blocked.email)


def test_blocked_domain_name_uniqueness(db):
    blocked = BlockedDomainNameFactory()
    with pytest.raises(IntegrityError):
        BlockedDomainNameFactory(domain=blocked.domain)
