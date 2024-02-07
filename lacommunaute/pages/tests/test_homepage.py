import pytest  # noqa
from django.test import override_settings
from django.urls import reverse

from lacommunaute.forum.enums import Kind as ForumKind
from lacommunaute.forum.factories import ForumFactory
from lacommunaute.forum_conversation.factories import PostFactory, TopicFactory


def test_context_data(client, db):
    topic = TopicFactory(with_post=True, forum=ForumFactory())
    news = TopicFactory(with_post=True, forum=ForumFactory(kind=ForumKind.NEWS))
    article = ForumFactory(parent=ForumFactory(type=1))

    disapproved_topic = TopicFactory(with_post=True, forum=ForumFactory())
    disapproved_topic.approved = False
    disapproved_topic.save()
    TopicFactory(with_post=True, forum=ForumFactory(kind=ForumKind.PRIVATE_FORUM))

    url = reverse("pages:home")

    response = client.get(url)
    assert response.status_code == 200

    assert response.context_data["topics_public"].get() == topic
    assert response.context_data["topics_newsfeed"].get() == news
    assert response.context_data["forums_category"].get() == article


def test_new_topics_order(client, db):
    topic1 = TopicFactory(with_post=True, forum=ForumFactory())
    topic2 = TopicFactory(with_post=True, forum=ForumFactory())
    url = reverse("pages:home")

    response = client.get(url)
    assert response.status_code == 200
    assert list(response.context_data["topics_public"]) == [topic2, topic1]

    PostFactory(topic=topic1)

    response = client.get(url)
    assert response.status_code == 200
    assert list(response.context_data["topics_public"]) == [topic2, topic1]


def test_highlighted_forum(client, db):
    forum = ForumFactory()
    url = reverse("pages:home")

    with override_settings(HIGHLIGHTED_FORUM_PK=None):
        response = client.get(url)
    assert "highlighted_forum" not in response.context_data
    assert "topics_of_highlighted_forum" not in response.context_data

    with override_settings(HIGHLIGHTED_FORUM_PK=forum.pk):
        response = client.get(url)
    assert "highlighted_forum" in response.context_data
    assert "topics_of_highlighted_forum" in response.context_data

    with override_settings(HIGHLIGHTED_FORUM_PK=999):
        response = client.get(url)
    assert "highlighted_forum" not in response.context_data
    assert "topics_of_highlighted_forum" not in response.context_data
