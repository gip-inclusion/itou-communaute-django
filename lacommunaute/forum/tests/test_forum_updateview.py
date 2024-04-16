import pytest  # noqa
from django.urls import reverse
from pytest_django.asserts import assertContains

from lacommunaute.users.factories import UserFactory
from lacommunaute.forum.factories import ForumFactory


def test_user_access(client, db):
    forum = ForumFactory()
    url = reverse("forum_extension:edit_forum", kwargs={"pk": forum.pk, "slug": forum.slug})
    response = client.get(url)
    assert response.status_code == 302

    user = UserFactory()
    client.force_login(user)
    response = client.get(url)
    assert response.status_code == 403

    user.is_staff = True
    user.save()
    response = client.get(url)
    assert response.status_code == 403

    user.is_superuser = True
    user.save()
    response = client.get(url)
    assert response.status_code == 200


def test_context_data(client, db):
    client.force_login(UserFactory(is_superuser=True))
    forum = ForumFactory()
    url = reverse("forum_extension:edit_forum", kwargs={"pk": forum.pk, "slug": forum.slug})
    response = client.get(url)
    assertContains(response, f"Mettre à jour le forum {forum.name}", html=True)
    assertContains(response, reverse("forum_extension:forum", kwargs={"pk": forum.pk, "slug": forum.slug}))
