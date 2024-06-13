import pytest  # noqa
from django.urls import reverse

from lacommunaute.forum.factories import ForumFactory
from lacommunaute.forum.models import ForumRating
from lacommunaute.users.factories import UserFactory


@pytest.fixture(name="public_forum")
def fixture_public_forum(db):
    return ForumFactory(with_public_perms=True)


def test_get_forum_rating_view(client, db, public_forum):
    response = client.get(reverse("forum_extension:rate", kwargs={"pk": public_forum.pk, "slug": public_forum.slug}))
    assert response.status_code == 405


def test_anonymous_post_forum_rating_view(client, db, public_forum):
    client.session.save()

    response = client.post(
        reverse("forum_extension:rate", kwargs={"pk": public_forum.pk, "slug": public_forum.slug}),
        data={"rating": "5"},
    )
    assert response.status_code == 200
    assert response.context["forum"] == public_forum
    assert response.context["rating"] == 5

    forum_rating = ForumRating.objects.get()
    assert forum_rating.forum == public_forum
    assert forum_rating.user is None
    assert forum_rating.rating == 5
    assert forum_rating.session_id == client.session.session_key


def test_authenticated_post_forum_rating_view(client, db, public_forum):
    user = UserFactory()
    client.force_login(user)

    response = client.post(
        reverse("forum_extension:rate", kwargs={"pk": public_forum.pk, "slug": public_forum.slug}),
        data={"rating": "1"},
    )
    assert response.status_code == 200

    forum_rating = ForumRating.objects.get()
    assert forum_rating.forum == public_forum
    assert forum_rating.user == user
    assert forum_rating.rating == 1
    assert forum_rating.session_id == client.session.session_key
