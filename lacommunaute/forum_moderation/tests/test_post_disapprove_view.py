import pytest  # noqa

from django.urls import reverse

from lacommunaute.forum_conversation.factories import TopicFactory, AnonymousPostFactory
from lacommunaute.forum_conversation.models import Post
from lacommunaute.forum_moderation.models import BlockedEmail, BlockedPost
from lacommunaute.users.factories import UserFactory
from lacommunaute.forum_moderation.enums import BlockedPostReason
from lacommunaute.forum_moderation.factories import BlockedEmailFactory


def test_post_disapprove_view(client, db):
    disapproved_post = AnonymousPostFactory(topic=TopicFactory(approved=False))
    client.force_login(UserFactory(is_superuser=True))
    response = client.post(
        reverse("forum_moderation_extension:disapprove_queued_post", kwargs={"pk": disapproved_post.pk})
    )
    assert response.status_code == 302
    assert BlockedEmail.objects.get(email=disapproved_post.username)

    # the original Post should be deleted, but a BlockedPost saved
    assert Post.objects.count() == 0
    blocked_post = BlockedPost.objects.get()
    assert blocked_post.content == str(disapproved_post.content)
    assert blocked_post.username == disapproved_post.username
    assert blocked_post.block_reason == BlockedPostReason.MODERATOR_DISAPPROVAL


def test_post_disapprove_view_with_existing_blocked_email(client, db):
    disapproved_post = AnonymousPostFactory(topic=TopicFactory(approved=False))
    BlockedEmailFactory(email=disapproved_post.username)
    client.force_login(UserFactory(is_superuser=True))
    response = client.post(
        reverse("forum_moderation_extension:disapprove_queued_post", kwargs={"pk": disapproved_post.pk})
    )
    assert response.status_code == 302
    assert BlockedEmail.objects.get(email=disapproved_post.username)
