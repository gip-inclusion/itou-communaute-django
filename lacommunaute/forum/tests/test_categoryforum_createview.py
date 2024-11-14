from django.urls import reverse
from machina.core.db.models import get_model
from pytest_django.asserts import assertContains

from lacommunaute.forum.models import Forum
from lacommunaute.users.factories import UserFactory


UserForumPermission = get_model("forum_permission", "UserForumPermission")


def test_user_access(client, db):
    url = reverse("forum_extension:create_category")
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


def test_form_title_and_context_data(client, db):
    client.force_login(UserFactory(is_superuser=True))
    url = reverse("forum_extension:create_category")
    response = client.get(url)
    assertContains(response, "Créer une nouvelle catégorie documentaire")
    assertContains(response, reverse("forum_extension:documentation"))


def test_success_url(client, db):
    client.force_login(UserFactory(is_superuser=True))
    url = reverse("forum_extension:create_category")
    response = client.post(url, data={"name": "Test", "description": "Test", "short_description": "Test"})
    assert response.status_code == 302
    assert response.url == reverse("forum_extension:documentation")


def test_create_category_with_perms(client, db):
    client.force_login(UserFactory(is_superuser=True))
    url = reverse("forum_extension:create_category")
    response = client.post(url, data={"name": "Test", "description": "Test", "short_description": "Test"})
    assert response.status_code == 302

    forum = Forum.objects.get()
    assert forum.type == Forum.FORUM_CAT
    assert forum.parent is None

    assert UserForumPermission.objects.filter(forum=forum).count() == 14
