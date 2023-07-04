import pytest  # noqa
from django.urls import reverse

from lacommunaute.forum.enums import Kind as ForumKind
from lacommunaute.forum.factories import ForumFactory
from lacommunaute.forum.models import Forum


def test_context(client, db):
    url = reverse("forum_extension:categories")
    response = client.get(url)
    assert response.status_code == 200
    assert "forum/category_forum_list.html" == response.templates[0].name


def test_queryset(client, db):
    forum = ForumFactory(type=Forum.FORUM_CAT)
    unvisible_forums = (
        ForumFactory(type=Forum.FORUM_CAT, parent=forum),
        ForumFactory(type=Forum.FORUM_CAT, kind=ForumKind.PRIVATE_FORUM),
        ForumFactory(),
        ForumFactory(type=Forum.FORUM_LINK),
    )
    url = reverse("forum_extension:categories")
    response = client.get(url)
    assert response.status_code == 200
    assert forum in response.context_data["forums"]
    for unvisible_forum in unvisible_forums:
        assert unvisible_forum not in response.context_data["forums"]
