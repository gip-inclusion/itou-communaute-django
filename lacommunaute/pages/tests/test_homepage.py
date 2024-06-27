import pytest  # noqa
from dateutil.relativedelta import relativedelta
from django.urls import reverse
from django.utils import timezone
from pytest_django.asserts import assertContains, assertNotContains

from lacommunaute.edito.factories import EditoFactory
from lacommunaute.event.factories import EventFactory
from lacommunaute.forum.enums import Kind as ForumKind
from lacommunaute.forum.factories import ForumFactory
from lacommunaute.forum_conversation.factories import PostFactory, TopicFactory
from lacommunaute.utils.testing import parse_response_to_soup


def test_context_data(client, db):
    topic = TopicFactory(with_post=True, forum=ForumFactory())
    article = ForumFactory(parent=ForumFactory(type=1))
    edito = EditoFactory()

    disapproved_topic = TopicFactory(with_post=True, forum=ForumFactory())
    disapproved_topic.approved = False
    disapproved_topic.save()
    TopicFactory(with_post=True, forum=ForumFactory(kind=ForumKind.PRIVATE_FORUM))

    url = reverse("pages:home")

    response = client.get(url)
    assert response.status_code == 200

    assert response.context_data["topics_public"].get() == topic
    assert response.context_data["forums_category"].get() == article
    assert response.context_data["edito"] == edito


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


def test_page_title(db, client):
    response = client.get(reverse("pages:home"))
    assertContains(response, "<title>Accueil- La communauté de l'inclusion</title>", html=True, count=1)


def test_events(db, client):
    old_event = EventFactory(date=timezone.now() - relativedelta(days=1))
    visible_future_event = EventFactory.create_batch(4, date=timezone.now() + relativedelta(days=1))
    unvisible_future_event = EventFactory(date=timezone.now() + relativedelta(days=1))
    response = client.get(reverse("pages:home"))
    assertContains(response, "Les évènements à venir", count=1)
    assertNotContains(response, old_event.name)
    for future_event in visible_future_event:
        assertContains(response, future_event.name)
        assertContains(response, reverse("event:detail", kwargs={"pk": future_event.pk}))
    assertNotContains(response, unvisible_future_event.name)
    assertContains(response, reverse("event:current"))


def test_edito(db, client, snapshot):
    EditoFactory()
    EditoFactory(for_snapshot=True)

    url = reverse("pages:home")

    response = client.get(url)
    assert response.status_code == 200
    assert str(parse_response_to_soup(response, selector=".s-section__container")) == snapshot(name="edito")
