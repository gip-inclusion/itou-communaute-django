import pytest
from django.test import override_settings
from django.urls import reverse

from lacommunaute.event.factories import EventFactory
from lacommunaute.forum.factories import ForumFactory
from lacommunaute.forum_conversation.factories import TopicFactory
from lacommunaute.users.factories import UserFactory
from lacommunaute.utils.enums import Environment
from lacommunaute.utils.testing import parse_response_to_soup


@pytest.mark.parametrize(
    "env,expected",
    [
        (None, False),
        (Environment.PROD, False),
        (Environment.TEST, True),
        (Environment.DEV, True),
    ],
)
def test_prod_environment(client, db, env, expected, snapshot):
    with override_settings(ENVIRONMENT=env):
        response = client.get("/")
    assert ('id="debug-mode-banner"' in response.content.decode()) == expected
    if expected:
        content = parse_response_to_soup(response, selector="#debug-mode-banner")
        assert str(content) == snapshot(name=env.label)


def test_exposed_settings(client, db):
    response = client.get("/")
    assert "BASE_TEMPLATE" in response.context
    assert "MATOMO_SITE_ID" in response.context
    assert "MATOMO_BASE_URL" in response.context
    assert "ENVIRONMENT" in response.context
    assert "EMPLOIS_PRESCRIBER_SEARCH" in response.context
    assert "EMPLOIS_COMPANY_SEARCH" in response.context


def test_matomo(client, settings, db, snapshot):
    """Test on a canically problematic view that we get the right Matomo properties.

    Namely, verify that the URL params are cleaned, sorted, the title is forced, and
    the path params are replaced by a the variadic version.

    Also ensure the user ID is correctly set.
    """
    settings.MATOMO_BASE_URL = "https://fake.matomo.url"
    user = UserFactory()
    client.force_login(user)

    # An unknown url is always resolved into a django flatpage
    response = client.get("/doesnotexist?token=blah&mtm_foo=truc", follow=True)
    assert response.context["matomo_custom_url"] == "^(?P<url>.*/)$?mtm_foo=truc"
    assert response.status_code == 404

    # A forum url
    forum = ForumFactory()
    response = client.get(reverse("forum_extension:forum", kwargs={"slug": forum.slug, "pk": forum.pk}))
    assert response.context["matomo_custom_url"] == f"forum/{forum.slug}-{forum.pk}/"

    # A topic url
    topic = TopicFactory(forum=forum, with_post=True)
    response = client.get(
        reverse(
            "forum_conversation:topic",
            kwargs={"forum_slug": forum.slug, "forum_pk": forum.pk, "slug": topic.slug, "pk": topic.pk},
        )
    )
    assert response.context["matomo_custom_url"] == f"forum/{forum.slug}-{forum.pk}/topic/<str:slug>-<int:pk>/"

    # Any other url
    event = EventFactory()
    url = reverse("event:detail", kwargs={"pk": event.pk})
    response = client.get(f"{url}?foo=bar&mtm_foo=truc&mtm_bar=bidule")
    assert response.status_code == 200
    assert response.context["matomo_custom_url"] == "calendar/<int:pk>/?mtm_bar=bidule&mtm_foo=truc"
