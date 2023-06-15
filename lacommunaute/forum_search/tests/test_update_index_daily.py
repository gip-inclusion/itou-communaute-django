import pytest
from django.core.management import call_command
from django.urls import reverse

from lacommunaute.forum.factories import ForumFactory
from lacommunaute.forum_conversation.factories import TopicFactory


@pytest.fixture
def search_url():
    return reverse("forum_search_extension:search")


@pytest.fixture
def forum():
    return ForumFactory(with_public_perms=True)


def test_recent_updated_forum_is_added_to_index(client, db, search_url, forum):
    call_command("update_index", age=1)

    query = forum.description.raw.split()[:4]
    response = client.get(search_url, {"q": " ".join(query)})

    assert response.status_code == 200
    for word in query:
        assert f'<span class="highlighted">{word}</span>' in response.content.decode("utf-8")


def test_recent_updated_post_is_added_to_index(client, db, search_url, forum):
    topic = TopicFactory(forum=forum, with_post=True)

    call_command("update_index", age=1)

    query = topic.first_post.content.raw.split()[:4]
    response = client.get(search_url, {"q": " ".join(query)})

    assert response.status_code == 200
    for word in query:
        assert f'<span class="highlighted">{word}</span>' in response.content.decode("utf-8")
