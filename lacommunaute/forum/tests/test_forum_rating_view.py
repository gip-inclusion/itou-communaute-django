import pytest
from django.urls import reverse

from lacommunaute.forum.factories import ForumFactory
from lacommunaute.forum.models import ForumRating
from lacommunaute.users.factories import UserFactory
from lacommunaute.utils.testing import parse_response_to_soup


@pytest.fixture(name="forum")
def fixture_forum(db):
    return ForumFactory()


def test_get_forum_rating_view(client, db, forum):
    response = client.get(reverse("forum_extension:rate", kwargs={"pk": forum.pk, "slug": forum.slug}))
    assert response.status_code == 405


def test_anonymous_post_forum_rating_view(client, db, forum, snapshot):
    client.session.save()

    response = client.post(
        reverse("forum_extension:rate", kwargs={"pk": forum.pk, "slug": forum.slug}),
        data={"rating": "5"},
    )
    assert response.status_code == 200
    assert response.context["forum"] == forum
    assert response.context["rating"] == 5
    content = parse_response_to_soup(response, replace_in_href=[forum])
    assert str(content) == snapshot(name="anonymous_post_forum_rating_view")

    forum_rating = ForumRating.objects.get()
    assert forum_rating.forum == forum
    assert forum_rating.user is None
    assert forum_rating.rating == 5
    assert forum_rating.session_id == client.session.session_key


def test_authenticated_post_forum_rating_view(client, db, forum, snapshot):
    user = UserFactory()
    client.force_login(user)

    response = client.post(
        reverse("forum_extension:rate", kwargs={"pk": forum.pk, "slug": forum.slug}),
        data={"rating": "1"},
    )
    assert response.status_code == 200
    content = parse_response_to_soup(response, replace_in_href=[forum])
    assert str(content) == snapshot(name="authenticated_post_forum_rating_view")

    forum_rating = ForumRating.objects.get()
    assert forum_rating.forum == forum
    assert forum_rating.user == user
    assert forum_rating.rating == 1
    assert forum_rating.session_id == client.session.session_key
