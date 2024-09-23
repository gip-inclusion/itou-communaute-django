import pytest  # noqa
from django.urls import reverse
from pytest_django.asserts import assertContains

from lacommunaute.forum.factories import CategoryForumFactory, ForumFactory


def test_display_banners(client, db):
    forum = CategoryForumFactory(with_child=True, with_public_perms=True)
    ForumFactory(parent=forum, with_public_perms=True, with_image=True)
    url = reverse("forum_extension:forum", kwargs={"pk": forum.pk, "slug": forum.slug})
    response = client.get(url)
    for child in forum.get_children():
        assertContains(response, child.image.url.split("=")[0])
