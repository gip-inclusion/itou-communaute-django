import pytest  # noqa
from django.urls import reverse
from machina.core.db.models import get_model
from pytest_django.asserts import assertContains

from lacommunaute.forum.enums import Kind as ForumKind
from lacommunaute.forum.models import Forum
from lacommunaute.users.factories import UserFactory
from lacommunaute.forum.factories import CategoryForumFactory


UserForumPermission = get_model("forum_permission", "UserForumPermission")


def test_user_access(client, db):
    category_forum = CategoryForumFactory()
    url = reverse("forum_extension:create_subcategory", kwargs={"pk": category_forum.pk})
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


def test_form_title_and_context_datas(client, db):
    client.force_login(UserFactory(is_superuser=True))
    category_forum = CategoryForumFactory()
    url = reverse("forum_extension:create_subcategory", kwargs={"pk": category_forum.pk})
    response = client.get(url)
    assertContains(response, f"Créer une fiche pratique dans la catégorie {category_forum.name}", html=True)
    assertContains(
        response, reverse("forum_extension:forum", kwargs={"pk": category_forum.pk, "slug": category_forum.slug})
    )


def test_success_url(client, db):
    client.force_login(UserFactory(is_superuser=True))
    category_forum = CategoryForumFactory()
    url = reverse("forum_extension:create_subcategory", kwargs={"pk": category_forum.pk})
    response = client.post(url, data={"name": "Test", "description": "Test", "short_description": "Test"})
    assert response.status_code == 302
    assert response.url == reverse(
        "forum_extension:forum", kwargs={"pk": category_forum.children.first().pk, "slug": "test"}
    )


def test_create_subcategory_with_perms(client, db):
    client.force_login(UserFactory(is_superuser=True))
    category_forum = CategoryForumFactory()
    url = reverse("forum_extension:create_subcategory", kwargs={"pk": category_forum.pk})
    response = client.post(url, data={"name": "Test", "description": "Test", "short_description": "Test"})
    assert response.status_code == 302

    forum = category_forum.children.get()
    assert forum.type == Forum.FORUM_POST
    assert forum.kind == ForumKind.PUBLIC_FORUM
    assert forum.parent == category_forum

    assert UserForumPermission.objects.filter(forum=forum).count() == 14
