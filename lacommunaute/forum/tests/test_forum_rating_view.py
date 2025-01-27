import pytest
from django.urls import reverse

from lacommunaute.forum.factories import ForumFactory
from lacommunaute.forum.models import ForumRating
from lacommunaute.users.factories import UserFactory
from lacommunaute.utils.testing import parse_response_to_soup


@pytest.fixture(name="public_forum")
def fixture_public_forum(db):
    return ForumFactory(with_public_perms=True)


def test_get_forum_rating_view(client, db, public_forum):
    response = client.get(reverse("forum_extension:rate", kwargs={"pk": public_forum.pk, "slug": public_forum.slug}))
    assert response.status_code == 405


@pytest.mark.parametrize(
    "user,rating, snapshot_name",
    [
        (None, 5, "anonymous_post_forum_rating_view"),
        (lambda: UserFactory(), 1, "authenticated_post_forum_rating_view"),
    ],
)
def test_post_forum_rating_view(client, db, public_forum, user, rating, snapshot_name, snapshot):
    if user:
        user = user()
        client.force_login(user)
    else:
        client.session.save()

    response = client.post(
        reverse("forum_extension:rate", kwargs={"pk": public_forum.pk, "slug": public_forum.slug}),
        data={"rating": rating},
    )
    assert response.status_code == 200
    content = parse_response_to_soup(response, replace_in_href=[public_forum])
    assert str(content) == snapshot(name=snapshot_name)

    forum_rating = ForumRating.objects.get()
    assert forum_rating.forum == public_forum
    assert forum_rating.rating == rating
    assert forum_rating.session_id == client.session.session_key
    if user:
        assert forum_rating.user == user
    else:
        assert forum_rating.user is None
