import re

import pytest
from dateutil.relativedelta import relativedelta
from django.urls import reverse
from django.utils import timezone
from pytest_django.asserts import assertContains, assertNotContains

from lacommunaute.event.factories import EventFactory
from lacommunaute.forum.factories import CategoryForumFactory, ForumFactory
from lacommunaute.forum_conversation.factories import TopicFactory
from lacommunaute.utils.testing import parse_response_to_soup


def _sub_svg_suffix(content):
    return re.sub(r"\.\w+\.svg", ".svg", content)


def test_context_data(client, db):
    article = ForumFactory(parent=ForumFactory(type=1))
    url = reverse("pages:home")

    response = client.get(url)
    assert response.status_code == 200

    assert response.context_data["forums_category"].get() == article


def test_page_title_header_footer(db, client, snapshot):
    response = client.get(reverse("pages:home"))
    assert response.status_code == 200

    assert str(parse_response_to_soup(response, selector="title")) == snapshot(name="homepage_title")

    header = _sub_svg_suffix(str(parse_response_to_soup(response, selector="header")))
    assert header == snapshot(name="homepage_header")

    footer = _sub_svg_suffix(str(parse_response_to_soup(response, selector="footer")))
    assert footer == snapshot(name="homepage_footer")


def test_events(db, client):
    old_event = EventFactory(date=timezone.now() - relativedelta(days=1))
    visible_future_event = EventFactory.create_batch(4, date=timezone.now() + relativedelta(days=1))
    unvisible_future_event = EventFactory(date=timezone.now() + relativedelta(days=1))
    response = client.get(reverse("pages:home"))
    assertContains(response, "Les prochains évènements", count=1)
    assertNotContains(response, old_event.name)
    for future_event in visible_future_event:
        assertContains(response, future_event.name)
        assertContains(response, reverse("event:detail", kwargs={"pk": future_event.pk}))
    assertNotContains(response, unvisible_future_event.name)
    assertContains(response, reverse("event:current"))


@pytest.mark.parametrize("nb_topics,nb_expected", [(i, i) for i in range(5)] + [(i, 4) for i in range(5, 7)])
def test_unsanswered_topics(db, client, nb_topics, nb_expected, snapshot):
    TopicFactory.create_batch(nb_topics, with_post=True, with_tags=["Pirmadienis", "Poniedziałek", "Lundi", "Montag"])
    response = client.get(reverse("pages:home"))
    assert len(response.context_data["unanswered_topics"]) == nb_expected
    assert ('id="unanswered_topics"' in str(response.content)) == (nb_expected > 0)


def test_numqueries(db, client, django_assert_num_queries):
    savepoint_queries = 4
    session_queries = 2
    with django_assert_num_queries(
        savepoint_queries
        + session_queries
        + 1  # get first public forum
        + 1  # get most recent updated forums in documentation
        + 1  # get unanswered topics
        + 1  # get upcoming events
    ):
        client.get(reverse("pages:home"))


def test_updated_forum_short_description(client, db, snapshot):
    parent = CategoryForumFactory()
    forum = ForumFactory(
        name="84, rue Georges",
        short_description="C'était partout, dans le monde entier, des centaines ou des milliers de millions de gens "
        "s'ignorant les uns les autres, séparés par des murs de haine et de mensonges, et cependant presque exactement"
        " les mêmes, des gens qui n'avaient jamais appris à penser, mais qui emmagasinaient dans leurs cœurs, leurs ve"
        "ntres et leurs muscles, la force qui, un jour, bouleverserait le monde.",
        parent=parent,
    )

    response = client.get(reverse("pages:home"))
    content = parse_response_to_soup(response, selector="#updated_forums", replace_in_href=[forum])
    assert str(content) == snapshot(name="truncated_encoded_short_description")
