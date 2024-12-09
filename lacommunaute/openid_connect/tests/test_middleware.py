import pytest
from django.urls import reverse
from pytest_django.asserts import assertRedirects, assertTemplateUsed

from lacommunaute.users.factories import UserFactory


@pytest.mark.parametrize(
    "params,expected",
    [
        ("?proconnect_login=true", ""),
        ("?proconnect_login=true&param=1", "?param=1"),
        ("?param=1&proconnect_login=true", "?param=1"),
    ],
)
def test_redirect_for_authenticated_user(client, db, params, expected):
    client.force_login(UserFactory())
    response = client.get(f"/{params}")
    assertRedirects(response, f"/{expected}")


@pytest.mark.parametrize(
    "params,expected",
    [
        ("?proconnect_login=true", "/"),
        ("?proconnect_login=true&param=1", "/?param=1"),
        ("?param=1&proconnect_login=true", "/?param=1"),
    ],
)
def test_redirect_for_anonymous_user(client, db, params, expected):
    response = client.get(f"/{params}")
    assertRedirects(response, f"{reverse('openid_connect:authorize')}?next={expected}", fetch_redirect_response=False)


@pytest.mark.parametrize(
    "params, logged",
    [
        ("", True),
        ("?param=1", True),
        ("?param=1&key=2", True),
        ("", False),
        ("?param=1", False),
        ("?param=1&key=2", False),
    ],
)
def test_wo_proconnect_login_param(client, db, logged, params):
    if logged:
        client.force_login(UserFactory())
    response = client.get(f"/{params}")
    assertTemplateUsed(response, "pages/home.html")
