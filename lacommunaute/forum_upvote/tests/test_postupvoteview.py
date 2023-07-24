import pytest  # noqa
from django.contrib.contenttypes.models import ContentType
from django.urls import reverse
from machina.core.db.models import get_model

from lacommunaute.forum.factories import ForumFactory
from lacommunaute.forum_conversation.factories import TopicFactory
from lacommunaute.forum_upvote.models import UpVote
from lacommunaute.users.factories import UserFactory


ForumReadTrack = get_model("forum_tracking", "ForumReadTrack")
url = reverse("forum_upvote:post")


def test_get(client, db):
    response = client.get(url)
    assert response.status_code == 405


def test_upvote_without_permission(client, db):
    topic = TopicFactory(with_post=True)
    form_data = {"pk": topic.first_post.pk}
    client.force_login(UserFactory())
    response = client.post(url, data=form_data)
    assert response.status_code == 403


def test_upvote_with_permission(client, db):
    user = UserFactory()
    topic = TopicFactory(with_post=True, forum=ForumFactory(with_public_perms=True))
    form_data = {"pk": topic.first_post.pk}
    client.force_login(user)

    # upvote
    response = client.post(url, data=form_data)
    assert response.status_code == 200
    assert '<i class="ri-bookmark-fill" aria-hidden="true"></i><span class="ml-1">1</span>' in str(response.content)
    assert UpVote.objects.get(
        voter_id=user.id,
        object_id=topic.first_post.id,
        content_type=ContentType.objects.get_for_model(topic.first_post),
    )

    # downvote
    response = client.post(url, data=form_data)
    assert response.status_code == 200
    assert '<i class="ri-bookmark-line" aria-hidden="true"></i><span class="ml-1">0</span>' in str(response.content)
    assert not UpVote.objects.all()


def test_object_not_found(client, db):
    form_data = {"pk": 9999}
    client.force_login(UserFactory())
    response = client.post(url, data=form_data)
    assert response.status_code == 404
    assert not UpVote.objects.all()


def test_mark_as_read(client, db):
    user = UserFactory()
    topic = TopicFactory(with_post=True, forum=ForumFactory(with_public_perms=True))
    form_data = {"pk": topic.first_post.pk}
    client.force_login(user)
    response = client.post(url, data=form_data)
    assert response.status_code == 200
    assert ForumReadTrack.objects.get(user_id=user.id, forum_id=topic.forum.id)


def test_context(client, db):
    topic = TopicFactory(with_post=True, forum=ForumFactory(with_public_perms=True))
    form_data = {"pk": topic.first_post.pk}
    client.force_login(UserFactory())
    response = client.post(url, data=form_data)
    assert response.status_code == 200
    assert response.context["kind"] == "post"
    assert response.context["obj"] == topic.first_post
