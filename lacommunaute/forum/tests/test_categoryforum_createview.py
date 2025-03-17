from django.urls import reverse
from pytest_django.asserts import assertContains

from lacommunaute.forum.forms import ForumForm, SubCategoryForumUpdateForm
from lacommunaute.forum.models import Forum
from lacommunaute.users.factories import UserFactory


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
    assert response.status_code == 200


def test_form_title_and_context_data(client, db):
    client.force_login(UserFactory(is_in_staff_group=True))
    url = reverse("forum_extension:create_category")
    response = client.get(url)
    assertContains(response, "Créer une nouvelle catégorie documentaire")
    assertContains(response, reverse("forum_extension:documentation"))
    assert isinstance(response.context["form"], ForumForm)
    assert not isinstance(response.context["form"], SubCategoryForumUpdateForm)


def test_success_url(client, db):
    client.force_login(UserFactory(is_in_staff_group=True))
    url = reverse("forum_extension:create_category")
    response = client.post(url, data={"name": "Test", "description": "Test", "short_description": "Test"})
    assert response.status_code == 302
    assert response.url == reverse("forum_extension:documentation")

    forum = Forum.objects.get()
    assert forum.type == Forum.FORUM_CAT
    assert forum.parent is None
