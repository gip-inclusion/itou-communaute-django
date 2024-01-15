import urllib.parse

import pytest
from django.conf import settings
from django.core.management import call_command
from django.urls import reverse
from pytest_django.asserts import assertContains, assertNotContains

from lacommunaute.forum.enums import Kind as Forum_Kind
from lacommunaute.forum.factories import ForumFactory
from lacommunaute.forum_conversation.factories import TopicFactory


@pytest.fixture(scope="session", autouse=True)
def haystack_woosh_path_xdist_suffix_fixture(worker_id) -> None:
    for haystack_setting in settings.HAYSTACK_CONNECTIONS.values():
        if haystack_setting["ENGINE"] == "haystack.backends.whoosh_backend.WhooshEngine":
            haystack_setting["PATH"] = "_".join([haystack_setting["PATH"], worker_id])


@pytest.fixture(name="search_url")
def search_url_fixture():
    return reverse("forum_search_extension:search")


@pytest.fixture(name="public_forums")
def public_forums_fixture():
    forums = ForumFactory.create_batch(2, with_public_perms=True)
    call_command("rebuild_index", noinput=True, interactive=False)
    return forums


@pytest.fixture(name="public_topics")
def public_topics_fixture():
    topics = TopicFactory.create_batch(2, forum=ForumFactory(with_public_perms=True), with_post=True)
    call_command("rebuild_index", noinput=True, interactive=False)
    return topics


def test_search_on_post(client, db, search_url, public_topics):
    query = public_topics[0].first_post.content.raw.split()[:4]
    response = client.get(search_url, {"q": " ".join(query)})

    assertNotContains(response, public_topics[1].subject)
    for word in query:
        assertContains(response, f'<span class="highlighted">{word}</span>')


def test_search_on_forum(client, db, search_url, public_forums):
    query = public_forums[0].description.raw.split()[:3]
    response = client.get(search_url, {"q": " ".join(query)})

    assertNotContains(response, public_forums[1].description.raw)
    for word in query:
        assertContains(response, f'<span class="highlighted">{word}</span>')


def test_search_with_no_query(client, db, search_url):
    response = client.get(search_url)
    assertContains(response, '<input type="search" name="q"')


def test_empty_search(client, db, search_url):
    response = client.get(search_url, {"q": ""})
    assertContains(response, '<input type="search" name="q"')


def test_search_with_no_results(client, db, search_url):
    response = client.get(search_url, {"q": "test"})
    assertContains(response, "Aucun résultat")


def test_search_with_non_unicode_characters(client, db, search_url):
    encoded_char = urllib.parse.quote("\x1f")
    response = client.get(search_url, {"q": encoded_char})
    assertContains(response, "Aucun résultat")


def test_search_on_post_model_only(client, db, search_url, public_topics, public_forums):
    datas = {"m": "post"}

    query = public_topics[0].first_post.content.raw.split()[:4]
    datas["q"] = " ".join(query)

    response = client.get(search_url, datas)
    for word in query:
        assertContains(response, f'<span class="highlighted">{word}</span>')

    query = public_forums[0].description.raw.split()[:3]
    datas["q"] = " ".join(query)

    response = client.get(search_url, datas)
    for word in query:
        assertNotContains(response, f'<span class="highlighted">{word}</span>')


def test_search_on_forum_model_only(client, db, search_url, public_topics, public_forums):
    datas = {"m": "forum"}

    query = public_topics[0].first_post.content.raw.split()[:4]
    datas["q"] = " ".join(query)

    response = client.get(search_url, datas)
    for word in query:
        assertNotContains(response, f'<span class="highlighted">{word}</span>')

    query = public_forums[0].description.raw.split()[:3]
    datas["q"] = " ".join(query)

    response = client.get(search_url, datas)
    for word in query:
        assertContains(response, f'<span class="highlighted">{word}</span>')


def test_search_on_both_models(client, db, search_url, public_topics, public_forums):
    datas = {"m": "all"}

    query = public_topics[0].first_post.content.raw.split()[:4]
    datas["q"] = " ".join(query)

    response = client.get(search_url, datas)
    for word in query:
        assertContains(response, f'<span class="highlighted">{word}</span>')

    query = public_forums[0].description.raw.split()[:3]
    datas["q"] = " ".join(query)

    response = client.get(search_url, datas)
    for word in query:
        assertContains(response, f'<span class="highlighted">{word}</span>')


def test_non_public_forums_are_excluded(client, db, search_url):
    for i, kind in enumerate([kind for kind in Forum_Kind if kind != Forum_Kind.PUBLIC_FORUM]):
        ForumFactory(kind=kind, name=f"invisible {i}")
    call_command("rebuild_index", noinput=True, interactive=False)
    response = client.get(search_url, {"q": "invisible"})
    assertContains(response, "Aucun résultat")


def test_posts_from_non_public_forums_are_excluded(client, db, search_url):
    for i, kind in enumerate([kind for kind in Forum_Kind if kind != Forum_Kind.PUBLIC_FORUM]):
        TopicFactory(forum=ForumFactory(kind=kind), subject=f"invisible {i}", with_post=True)
    call_command("rebuild_index", noinput=True, interactive=False)
    response = client.get(search_url, {"q": "invisible"})
    assertContains(response, "Aucun résultat")


def test_unapproved_post_is_exclude(client, db, search_url, public_forums):
    topic = TopicFactory(forum=public_forums[0], with_post=True)
    topic.first_post.approved = False
    topic.first_post.save()
    call_command("rebuild_index", noinput=True, interactive=False)
    response = client.get(search_url, {"q": topic.first_post.content.raw.split()[0]})
    assertContains(response, "Aucun résultat")
