import pytest  # noqa
from django.urls import reverse

from lacommunaute.forum.enums import Kind as ForumKind
from lacommunaute.forum.factories import ForumFactory
from lacommunaute.forum_conversation.factories import TopicFactory


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
