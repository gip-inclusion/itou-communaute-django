import pytest  # noqa
from lacommunaute.forum_conversation.factories import TopicFactory, AnonymousPostFactory
from lacommunaute.notification.models import BouncedEmail
from lacommunaute.users.factories import UserFactory
from django.urls import reverse


def test_post_disapprove_view(client, db):
    disapproved_post = AnonymousPostFactory(topic=TopicFactory(approved=False))
    client.force_login(UserFactory(is_superuser=True))
    response = client.post(
        reverse("forum_moderation_extension:disapprove_queued_post", kwargs={"pk": disapproved_post.pk})
    )
    assert response.status_code == 302
    assert BouncedEmail.objects.get(email=disapproved_post.username)
