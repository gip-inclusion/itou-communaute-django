from django.urls import reverse
from machina.core.db.models import get_model
from pytest_django.asserts import assertContains

from lacommunaute.forum.factories import ForumFactory
from lacommunaute.forum_upvote.models import UpVote
from lacommunaute.users.factories import UserFactory


ForumReadTrack = get_model("forum_tracking", "ForumReadTrack")
url = reverse("forum_upvote:forum")


def test_get(client, db):
    response = client.get(url)
    assert response.status_code == 405


def test_upvote_downvote(client, db):
    user = UserFactory()
    forum = ForumFactory()
    form_data = {"pk": forum.pk}
    client.force_login(user)

    # upvote
    response = client.post(url, data=form_data)
    assertContains(
        response, '<i class="ri-notification-2-fill me-1" aria-hidden="true"></i><span>1</span>', status_code=200
    )
    assert UpVote.objects.get()

    # downvote
    response = client.post(url, data=form_data)
    assertContains(
        response, '<i class="ri-notification-2-line me-1" aria-hidden="true"></i><span>0</span>', status_code=200
    )
    assert not UpVote.objects.all()


def test_object_not_found(client, db):
    form_data = {"pk": 9999}
    client.force_login(UserFactory())
    response = client.post(url, data=form_data)
    assert response.status_code == 404
    assert not UpVote.objects.all()


def test_mark_as_read(client, db):
    user = UserFactory()
    forum = ForumFactory()
    form_data = {"pk": forum.pk}
    client.force_login(user)
    response = client.post(url, data=form_data)
    assert response.status_code == 200
    assert ForumReadTrack.objects.get(user_id=user.id, forum_id=forum.id)


def test_context(client, db):
    forum = ForumFactory()
    form_data = {"pk": forum.pk}
    client.force_login(UserFactory())
    response = client.post(url, data=form_data)
    assert response.status_code == 200
    assert response.context["kind"] == "forum"
    assert response.context["obj"] == forum
