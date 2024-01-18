import urllib.parse

import pytest
from django.conf import settings
from django.core.management import call_command
from django.urls import reverse
from pytest_django.asserts import assertContains, assertNotContains

from lacommunaute.forum.enums import Kind as Forum_Kind
from lacommunaute.forum.factories import ForumFactory
from lacommunaute.forum_conversation.factories import PostFactory, TopicFactory
from lacommunaute.utils.testing import parse_response_to_soup


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
    forum1 = ForumFactory.create(
        with_public_perms=True,
        name="Le PASS IAE",
        description="Tout savoir sur le PASS IAE, l’insertion par l’activité économique, et plus encore !",
        short_description="Tout savoir sur le PASS IAE",
    )
    topic1 = TopicFactory(forum=forum1, subject="Obtention d’un PASS IAE")
    PostFactory(
        topic=topic1,
        subject="Qui contacter ?",
        content="L’équipe des emplois de l’inclusion",
    )
    forum2 = ForumFactory.create(
        with_public_perms=True,
        name="Administrateur de structure",
        description="Gérer votre structure, ses membres, sa localisation et ses fiches de postes.",
        short_description="Gestion de la structure",
    )
    topic2 = TopicFactory(forum=forum2, subject="Inviter un collaborateur")
    PostFactory(
        topic=topic2,
        subject="Inviter ses collaborateurs par email",
        content="Listez les emails de vos collaborateurs, ils recevront un email avec les instructions.",
    )
    call_command("rebuild_index", noinput=True, interactive=False)
    return [forum1, forum2]


@pytest.fixture(name="public_topics")
def public_topics_fixture():
    forum = ForumFactory.create(
        with_public_perms=True,
        name="Le rôle de prescripteur",
        description="Explication du rôle de prescripteur, un acteur clé de l’insertion.",
        short_description="Détails du rôle de prescripteur",
    )
    topic1 = TopicFactory(forum=forum, subject="Qui sont les prescripteurs ?")
    PostFactory(
        topic=topic1,
        subject="Les missions locales",
        content="La mission locale est un espace d'intervention au service des jeunes.",
    )
    topic2 = TopicFactory(forum=forum, subject="Habilitation des prescripteurs")
    PostFactory(
        topic=topic2,
        subject="Demander une habilitation",
        content="La demande d’habilitation se fait auprès du préfet.",
    )
    call_command("rebuild_index", noinput=True, interactive=False)
    return [topic1, topic2]


def test_search_on_post(client, db, search_url, public_topics):
    query = ["au", "service", "des", "jeunes"]
    response = client.get(search_url, {"q": " ".join(query)})

    assertNotContains(response, "Demander une habilitation")
    for word in query:
        assertContains(response, f'<span class="highlighted">{word}</span>')


def test_search_on_forum(client, db, search_url, public_forums):
    query = ["Tout", "savoir", "sur"]
    response = client.get(search_url, {"q": " ".join(query)})

    assertNotContains(response, public_forums[1].description.raw)
    for word in query:
        assertContains(response, f'<span class="highlighted">{word}</span>')


def test_search_with_no_query(client, db, search_url):
    ForumFactory()
    response = client.get(search_url)
    assertContains(response, '<input type="search" name="q"')


def test_empty_search(client, db, search_url):
    ForumFactory()
    response = client.get(search_url, {"q": ""})
    assertContains(response, '<input type="search" name="q"')


def test_search_with_no_results(client, db, search_url):
    ForumFactory()
    response = client.get(search_url, {"q": "test"})
    assertContains(response, "Aucun résultat")


def test_search_with_non_unicode_characters(client, db, search_url):
    ForumFactory()
    encoded_char = urllib.parse.quote("\x1f")
    response = client.get(search_url, {"q": encoded_char})
    assertContains(response, "Aucun résultat")


def test_search_on_post_model_only(client, db, search_url, public_topics, public_forums):
    datas = {"m": "post"}

    query = ["La", "mission", "locale", "est"]
    datas["q"] = " ".join(query)

    response = client.get(search_url, datas)
    for word in query:
        assertContains(response, f'<span class="highlighted">{word}</span>')

    query = ["Tout", "savoir", "sur"]
    datas["q"] = " ".join(query)

    response = client.get(search_url, datas)
    for word in query:
        assertNotContains(response, f'<span class="highlighted">{word}</span>')


def test_search_on_forum_model_only(client, db, search_url, public_topics, public_forums):
    datas = {"m": "forum"}

    query = ["La", "mission", "locale", "est"]
    datas["q"] = " ".join(query)

    response = client.get(search_url, datas)
    for word in query:
        assertNotContains(response, f'<span class="highlighted">{word}</span>')

    query = ["Tout", "savoir", "sur"]
    datas["q"] = " ".join(query)

    response = client.get(search_url, datas)
    for word in query:
        assertContains(response, f'<span class="highlighted">{word}</span>')


def test_search_on_both_models(client, db, search_url, public_topics, public_forums):
    datas = {"m": "all"}
    query = ["La", "mission", "locale", "est"]
    datas["q"] = " ".join(query)

    response = client.get(search_url, datas)
    for word in query:
        assertContains(response, f'<span class="highlighted">{word}</span>')

    query = ["Tout", "savoir", "sur", "le"]
    datas["q"] = " ".join(query)

    response = client.get(search_url, datas)
    for word in query:
        assertContains(response, f'<span class="highlighted">{word}</span>')


def test_non_public_forums_are_excluded(client, db, search_url):
    ForumFactory()
    for i, kind in enumerate([kind for kind in Forum_Kind if kind != Forum_Kind.PUBLIC_FORUM]):
        ForumFactory(kind=kind, name=f"invisible {i}")
    call_command("rebuild_index", noinput=True, interactive=False)
    response = client.get(search_url, {"q": "invisible"})
    assertContains(response, "Aucun résultat")


def test_posts_from_non_public_forums_are_excluded(client, db, search_url):
    ForumFactory()
    for i, kind in enumerate([kind for kind in Forum_Kind if kind != Forum_Kind.PUBLIC_FORUM]):
        TopicFactory(forum=ForumFactory(kind=kind), subject=f"invisible {i}", with_post=True)
    call_command("rebuild_index", noinput=True, interactive=False)
    response = client.get(search_url, {"q": "invisible"})
    assertContains(response, "Aucun résultat")


def test_unapproved_post_is_exclude(client, db, search_url):
    forum = ForumFactory.create(
        with_public_perms=True,
        name="Le PASS IAE",
        description="Tout savoir sur le PASS IAE, l’insertion par l’activité économique, et plus encore !",
        short_description="Tout savoir sur le PASS IAE",
    )
    topic = TopicFactory(forum=forum, subject="Obtention d’un PASS IAE")
    PostFactory(
        topic=topic,
        approved=False,  # Not approved, should not appear in search results.
        subject="Qui contacter ?",
        content="L’équipe des emplois de l’inclusion",
    )
    call_command("rebuild_index", noinput=True, interactive=False)
    response = client.get(search_url, {"q": "emplois"})
    assertContains(response, "Aucun résultat")


def test_extra_context(client, db, search_url, snapshot):
    forum = ForumFactory()

    response = client.get(search_url)
    content = parse_response_to_soup(response, selector="main")
    assert str(content) == snapshot(name="no_query")

    datas = {"m": "post", "q": " ".join(["Bubba", "Gump", "Shrimp", "Co."])}
    response = client.get(search_url, datas)
    content = parse_response_to_soup(
        response, selector="main", replace_in_href=[(forum.slug, "forrest-gump"), (str(forum.pk), "42")]
    )
    assert str(content) == snapshot(name="no_results")
