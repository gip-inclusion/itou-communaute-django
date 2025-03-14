import pytest
from django.urls import reverse
from machina.core.loading import get_class
from pytest_django.asserts import assertContains

from lacommunaute.forum_conversation.factories import TopicFactory


assign_perm = get_class("forum_permission.shortcuts", "assign_perm")


@pytest.fixture(name="topic")
def topic_fixture():
    topic = TopicFactory(with_post=True)
    assign_perm("can_delete_posts", topic.poster, topic.forum)
    return topic


@pytest.fixture(name="url")
def url_fixture(topic):
    return reverse("forum_moderation_extension:topic_delete", kwargs={"slug": topic.slug, "pk": topic.pk})


def test_get_on_topic_delete_view(client, db, topic, url):
    client.force_login(topic.poster)
    response = client.get(url)
    assert response.status_code == 200
    assertContains(
        response,
        '<div class="mb-3 warning-message">Voulez-vous vraiment supprimer ce sujet ?</div>',
        status_code=200,
        html=True,
    )


def test_post_on_topic_delete_view(client, db, topic, url):
    client.force_login(topic.poster)
    response = client.post(url)
    assert response.status_code == 302
    assert response.url == reverse("pages:home")
    assert topic.forum.topics.count() == 0
