import pytest  # noqa
from django.urls import reverse
from pytest_django.asserts import assertContains

from lacommunaute.forum.enums import Kind as ForumKind
from lacommunaute.forum.factories import ForumFactory
from lacommunaute.forum.models import Forum


def test_context(client, db):
    url = reverse("forum_extension:documentation")
    response = client.get(url)
    assert "forum/category_forum_list.html" == response.templates[0].name
    assertContains(response, reverse("pages:statistiques"), status_code=200)


def test_queryset(client, db):
    forum = ForumFactory(type=Forum.FORUM_CAT)
    unvisible_forums = (
        ForumFactory(type=Forum.FORUM_CAT, parent=forum),
        ForumFactory(type=Forum.FORUM_CAT, kind=ForumKind.PRIVATE_FORUM),
        ForumFactory(),
        ForumFactory(type=Forum.FORUM_LINK),
    )
    url = reverse("forum_extension:documentation")
    response = client.get(url)
    assert response.status_code == 200
    assert forum in response.context_data["forums"]
    for unvisible_forum in unvisible_forums:
        assert unvisible_forum not in response.context_data["forums"]
