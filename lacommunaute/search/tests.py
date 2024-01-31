import urllib.parse

import pytest
from django.db import connection
from django.urls import reverse
from pytest_django.asserts import assertContains, assertNotContains

from lacommunaute.forum.enums import Kind as Forum_Kind
from lacommunaute.forum.factories import ForumFactory
from lacommunaute.forum_conversation.factories import PostFactory, TopicFactory
from lacommunaute.utils.testing import parse_response_to_soup


@pytest.fixture(name="search_url")
def search_url_fixture():
    return reverse("search:index")


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
    refresh_search_index()
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
    refresh_search_index()
    return [topic1, topic2]


def refresh_search_index():
    with connection.cursor() as c:
        c.execute("REFRESH MATERIALIZED VIEW search_commonindex;")


def test_search_on_post(client, db, search_url, public_topics):
    query = ["au", "service", "des", "jeunes"]
    response = client.get(search_url, {"q": " ".join(query)})

    assertNotContains(response, "Demander une habilitation")
    for word in ["service", "jeunes"]:  # Stop words are ignored, thus not highlighted.
        assertContains(response, f'<span class="highlighted">{word}</span>')


def test_search_on_forum(client, db, search_url, public_forums):
    query = ["Tout", "savoir", "sur"]
    response = client.get(search_url, {"q": " ".join(query)})

    assertNotContains(response, public_forums[1].description.raw)
    for word in ["Tout", "savoir"]:  # Stop words are ignored, thus not highlighted.
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
    datas = {"m": "TOPIC"}

    query = ["La", "mission", "locale", "est"]
    datas["q"] = " ".join(query)

    response = client.get(search_url, datas)
    for word in ["mission", "locale"]:  # Stop words are ignored, thus not highlighted.
        assertContains(response, f'<span class="highlighted">{word}</span>')

    query = ["Tout", "savoir", "sur"]
    datas["q"] = " ".join(query)

    response = client.get(search_url, datas)
    for word in ["Tout", "savoir"]:  # Stop words are ignored, thus not highlighted.
        assertNotContains(response, f'<span class="highlighted">{word}</span>')


def test_search_on_forum_model_only(client, db, search_url, public_topics, public_forums):
    datas = {"m": "FORUM"}

    query = ["La", "mission", "locale", "est"]
    datas["q"] = " ".join(query)

    response = client.get(search_url, datas)
    for word in ["mission", "locale"]:  # Stop words are ignored, thus not highlighted.
        assertNotContains(response, f'<span class="highlighted">{word}</span>')

    query = ["Tout", "savoir", "sur"]
    datas["q"] = " ".join(query)

    response = client.get(search_url, datas)
    for word in ["Tout", "savoir"]:  # Stop words are ignored, thus not highlighted.
        assertContains(response, f'<span class="highlighted">{word}</span>')


def test_search_on_both_models(client, db, search_url, public_topics, public_forums):
    datas = {"m": "all"}
    query = ["La", "mission", "locale", "est"]
    datas["q"] = " ".join(query)

    response = client.get(search_url, datas)
    for word in ["mission", "locale"]:  # Stop words are ignored, thus not highlighted.
        assertContains(response, f'<span class="highlighted">{word}</span>')

    query = ["Tout", "savoir", "sur", "le"]
    datas["q"] = " ".join(query)

    response = client.get(search_url, datas)
    for word in ["Tout", "savoir"]:  # Stop words are ignored, thus not highlighted.
        assertContains(response, f'<span class="highlighted">{word}</span>')


def test_non_public_forums_are_excluded(client, db, search_url):
    ForumFactory()
    for i, kind in enumerate([kind for kind in Forum_Kind if kind != Forum_Kind.PUBLIC_FORUM]):
        ForumFactory(kind=kind, name=f"invisible {i}")
    refresh_search_index()
    response = client.get(search_url, {"q": "invisible"})
    assertContains(response, "Aucun résultat")


def test_posts_from_non_public_forums_are_excluded(client, db, search_url):
    ForumFactory()
    for i, kind in enumerate([kind for kind in Forum_Kind if kind != Forum_Kind.PUBLIC_FORUM]):
        TopicFactory(forum=ForumFactory(kind=kind), subject=f"invisible {i}", with_post=True)
    refresh_search_index()
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
    refresh_search_index()
    response = client.get(search_url, {"q": "emplois"})
    assertContains(response, "Aucun résultat")


def test_extra_context(client, db, search_url, snapshot):
    forum = ForumFactory()

    response = client.get(search_url)
    content = parse_response_to_soup(response, selector="main")
    assert str(content) == snapshot(name="no_query")

    datas = {"m": "TOPIC", "q": " ".join(["Bubba", "Gump", "Shrimp", "Co."])}
    response = client.get(search_url, datas)
    content = parse_response_to_soup(
        response, selector="main", replace_in_href=[(forum.slug, "forrest-gump"), (str(forum.pk), "42")]
    )
    assert str(content) == snapshot(name="no_results")


def test_search_all_site_is_checked(client, db, search_url):
    response = client.get(search_url)
    assertContains(
        response,
        """
        <li class="list-inline-item me-3">
        <label for="id_m_0">
        <input type="radio" name="m" value="all" id="id_m_0" checked="">
        tout le site
        </label>
        </li>
        """,
        html=True,
        count=1,
    )


def test_pagination_perserves_get_params(client, db, search_url):
    forum = ForumFactory()
    topics = TopicFactory.create_batch(11, forum=forum, subject="Obtention d’un PASS IAE")
    for topic in topics:
        PostFactory(topic=topic, poster=topic.poster, subject=topic.subject)
    refresh_search_index()
    response = client.get(search_url, data={"m": "TOPIC", "q": "Obtention"})
    assertContains(
        response,
        f'<a href="{search_url}?m=TOPIC&amp;q=Obtention&amp;page=2" class="page-link">2</a>',
        count=1,
    )
