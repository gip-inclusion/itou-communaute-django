import pytest  # noqa


from lacommunaute.forum_conversation.factories import AnonymousPostFactory, TopicFactory
from lacommunaute.forum_moderation.utils import check_post_approbation
from lacommunaute.notification.factories import BouncedDomainNameFactory


def test_check_post_approbation(db):
    post = AnonymousPostFactory(topic=TopicFactory(), username='"spam@blocked"@scammers.com')
    post = check_post_approbation(post)
    assert post.update_reason is None
    assert post.approved is True

    BouncedDomainNameFactory(domain="scammers.com")
    post = check_post_approbation(post)
    assert post.update_reason == "Bounced Domain detected"
    assert post.approved is False
