from django.contrib.contenttypes.models import ContentType
from django.urls import reverse
from machina.core.db.models import get_model
from pytest_django.asserts import assertContains

from lacommunaute.forum_conversation.factories import TopicFactory
from lacommunaute.forum_upvote.models import UpVote
from lacommunaute.users.factories import UserFactory


ForumReadTrack = get_model("forum_tracking", "ForumReadTrack")
url = reverse("forum_upvote:post")


def test_get(client, db):
    response = client.get(url)
    assert response.status_code == 405


def test_upvote(client, db):
    user = UserFactory()
    topic = TopicFactory(with_post=True)
    form_data = {"pk": topic.first_post.pk}
    client.force_login(user)

    # upvote
    response = client.post(url, data=form_data)
    assertContains(
        response, '<i class="ri-notification-2-fill me-1" aria-hidden="true"></i><span>1</span>', status_code=200
    )
    assert UpVote.objects.get(
        voter_id=user.id,
        object_id=topic.first_post.id,
        content_type=ContentType.objects.get_for_model(topic.first_post),
    )

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
    topic = TopicFactory(with_post=True)
    form_data = {"pk": topic.first_post.pk}
    client.force_login(user)
    response = client.post(url, data=form_data)
    assert response.status_code == 200
    assert ForumReadTrack.objects.get(user_id=user.id, forum_id=topic.forum.id)


def test_context(client, db):
    topic = TopicFactory(with_post=True)
    form_data = {"pk": topic.first_post.pk}
    client.force_login(UserFactory())
    response = client.post(url, data=form_data)
    assert response.status_code == 200
    assert response.context["kind"] == "post"
    assert response.context["obj"] == topic.first_post
