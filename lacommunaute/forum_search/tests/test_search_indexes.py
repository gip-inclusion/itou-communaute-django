import urllib.parse

import pytest
from django.core.management import call_command
from django.urls import reverse

from lacommunaute.forum.factories import ForumFactory  # noqa F401
from lacommunaute.forum_conversation.factories import TopicFactory


@pytest.fixture
def search_url():
    return reverse("forum_search_extension:search")


@pytest.fixture
def public_topics():
    topics = TopicFactory.create_batch(2, forum=ForumFactory(with_public_perms=True), with_post=True)
    call_command("rebuild_index", noinput=True, interactive=False)
    return topics


def test_search_on_post(client, db, search_url, public_topics):
    query = public_topics[0].first_post.content.raw.split()[:4]
    response = client.get(search_url, {"q": " ".join(query)})

    assert response.status_code == 200
    assert public_topics[1].subject not in response.content.decode("utf-8")
    for word in query:
        assert f'<span class="highlighted">{word}</span>' in response.content.decode("utf-8")


def test_search_with_no_query(client, db, search_url):
    response = client.get(search_url)
    assert response.status_code == 200
    assert '<input type="search" name="q"' in response.content.decode("utf-8")


def test_empty_search(client, db, search_url):
    response = client.get(search_url, {"q": ""})
    assert response.status_code == 200
    assert '<input type="search" name="q"' in response.content.decode("utf-8")


def test_search_with_no_results(client, db, search_url):
    response = client.get(search_url, {"q": "test"})
    assert response.status_code == 200
    assert "Aucun résultat" in response.content.decode("utf-8")


def test_search_with_non_unicode_characters(client, db, search_url):
    encoded_char = urllib.parse.quote("\x1f")
    response = client.get(search_url, {"q": encoded_char})
    assert response.status_code == 200
    assert "Aucun résultat" in response.content.decode("utf-8")
