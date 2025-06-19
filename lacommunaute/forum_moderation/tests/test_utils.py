from faker import Faker

from lacommunaute.forum_conversation.factories import AnonymousPostFactory, TopicFactory
from lacommunaute.forum_moderation.enums import BlockedPostReason
from lacommunaute.forum_moderation.factories import BlockedDomainNameFactory, BlockedEmailFactory
from lacommunaute.forum_moderation.utils import check_post_approbation


faker = Faker()


def test_check_post_approbation_on_domain_name(db):
    post = AnonymousPostFactory(topic=TopicFactory(), username='"spam@blocked"@scammers.com')
    post = check_post_approbation(post)
    assert post.update_reason is None
    assert post.approved is True

    BlockedDomainNameFactory(domain="scammers.com")
    post = check_post_approbation(post)
    assert post.update_reason == "Blocked Domain detected"
    assert post.approved is False


def test_check_post_approbation_on_email(db):
    post = AnonymousPostFactory(topic=TopicFactory(), username="spam@yopmail.com")
    post = check_post_approbation(post)
    assert post.update_reason is None
    assert post.approved is True

    BlockedEmailFactory(email="spam@yopmail.com")
    post = check_post_approbation(post)
    assert post.update_reason == "Blocked Email detected"
    assert post.approved is False


def test_check_post_approbation_on_language_not_detected(db):
    post = AnonymousPostFactory(topic=TopicFactory(), content="40")
    post = check_post_approbation(post)
    assert post.update_reason is BlockedPostReason.ALTERNATIVE_LANGUAGE.label
    assert post.approved is False
