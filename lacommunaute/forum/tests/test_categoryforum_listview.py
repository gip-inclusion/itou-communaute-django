from django.urls import reverse
from pytest_django.asserts import assertContains, assertNotContains

from lacommunaute.forum.factories import CategoryForumFactory, ForumFactory
from lacommunaute.forum.models import Forum
from lacommunaute.users.factories import UserFactory


def test_context(client, db):
    url = reverse("forum_extension:documentation")
    response = client.get(url)
    assert "forum/category_forum_list.html" == response.templates[0].name
    assertContains(response, reverse("stats:statistiques"), status_code=200)


def test_queryset(client, db):
    forum = ForumFactory(type=Forum.FORUM_CAT)
    unvisible_forums = (
        ForumFactory(type=Forum.FORUM_CAT, parent=forum),
        ForumFactory(),
        ForumFactory(type=Forum.FORUM_LINK),
    )
    url = reverse("forum_extension:documentation")
    response = client.get(url)
    assert response.status_code == 200
    assert forum in response.context_data["forums"]
    for unvisible_forum in unvisible_forums:
        assert unvisible_forum not in response.context_data["forums"]


def test_display_create_category_button(client, db):
    url = reverse("forum_extension:documentation")
    response = client.get(url)
    assertNotContains(response, reverse("forum_extension:create_category"), status_code=200)

    user = UserFactory()
    client.force_login(user)
    response = client.get(url)
    assertNotContains(response, reverse("forum_extension:create_category"), status_code=200)

    user.is_staff = True
    user.save()
    response = client.get(url)
    assertContains(response, reverse("forum_extension:create_category"), status_code=200)


def test_display_banners(client, db):
    forum = CategoryForumFactory(with_child=True)
    ForumFactory(parent=forum, with_image=True)
    url = reverse("forum_extension:forum", kwargs={"pk": forum.pk, "slug": forum.slug})
    response = client.get(url)
    for child in forum.get_children():
        assertContains(response, child.image.url.split("=")[0])
