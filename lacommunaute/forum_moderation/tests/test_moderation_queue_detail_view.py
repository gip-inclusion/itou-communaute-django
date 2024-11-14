from django.urls import reverse
from pytest_django.asserts import assertContains

from lacommunaute.forum_conversation.factories import AnonymousPostFactory, TopicFactory
from lacommunaute.users.factories import UserFactory


def test_detail_view_for_anonymous_post(client, db):
    post = AnonymousPostFactory(topic=TopicFactory(approved=False), approved=False)
    client.force_login(UserFactory(is_superuser=True))
    response = client.get(reverse("forum_moderation:queued_post", kwargs={"pk": post.pk}))
    assertContains(response, post.poster_display_name)
    assertContains(response, post.topic.subject)


def test_detail_view_with_authenticated_post(client, db):
    topic = TopicFactory(approved=False, with_post=True)
    client.force_login(UserFactory(is_superuser=True))
    response = client.get(reverse("forum_moderation:queued_post", kwargs={"pk": topic.first_post.pk}))
    assertContains(response, topic.subject)
    assertContains(response, topic.first_post.poster_display_name)
