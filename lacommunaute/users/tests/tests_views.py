import json
import re
from unittest import mock
from urllib.parse import urlencode

import httpx
import pytest
import respx
from django.conf import settings
from django.contrib.auth.tokens import default_token_generator
from django.contrib.messages.api import get_messages
from django.contrib.messages.middleware import MessageMiddleware
from django.contrib.sessions.middleware import SessionMiddleware
from django.test import RequestFactory, override_settings
from django.urls import reverse
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from pytest_django.asserts import assertContains

from lacommunaute.forum_member.models import ForumProfile
from lacommunaute.notification.emails import SIB_SMTP_URL
from lacommunaute.users.enums import IdentityProvider
from lacommunaute.users.factories import UserFactory
from lacommunaute.users.models import User
from lacommunaute.users.views import send_magic_link
from lacommunaute.utils.enums import Environment
from lacommunaute.utils.testing import parse_response_to_soup
from lacommunaute.utils.urls import clean_next_url


next_url_tuples = [("/", "/"), ("/topics/", "/topics/"), ("http://www.unallowed_host.com", "/")]


@pytest.fixture(name="mock_respx_post_to_sib_smtp_url")
def mock_respx_post_to_sib_smtp_url_fixture():
    with respx.mock:
        respx.post(SIB_SMTP_URL).mock(return_value=httpx.Response(200, json={"message": "OK"}))
        yield


@pytest.fixture(name="mock_token_generator")
def mock_token_generator_fixture():
    with mock.patch.object(default_token_generator, "make_token", return_value="fixed-token"):
        yield default_token_generator


def custom_user_token(user, fixed_token=False):
    uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
    if fixed_token:
        token = "fixed-token"
    else:
        token = default_token_generator.make_token(user)
    return user, uidb64, token


@pytest.fixture(name="user")
def user_fixture():
    return UserFactory(
        first_name="Samuel",
        last_name="Jackson",
        email="samuel@jackson.com",
        identity_provider=IdentityProvider.PRO_CONNECT.value,
    )


@pytest.fixture(name="user_token")
def user_token_fixture(user):
    return custom_user_token(user)


@pytest.fixture(name="fixed_user_token")
def fixed_user_token_fixture(user):
    return custom_user_token(user, fixed_token=True)


def validate_magiclink_payload(payload_as_str, uidb64, token, expected):
    url = f"{settings.COMMU_PROTOCOL}://{settings.COMMU_FQDN}" + reverse(
        "users:login_with_link", kwargs={"uidb64": uidb64, "token": token}
    )
    payload = json.loads(payload_as_str)

    if payload["params"]["login_link"] == url + "?" + urlencode({"next": expected}):
        return True

    return False


class TestSendMagicLink:
    @pytest.mark.parametrize("env,count_msg", [(Environment.PROD, 0), (Environment.DEV, 1)])
    def test_send_magic_link(
        self, db, user, snapshot, mock_token_generator, mock_respx_post_to_sib_smtp_url, env, count_msg
    ):
        with override_settings(ENVIRONMENT=env):
            next_url = "/topics/"
            request = RequestFactory().get("/")
            SessionMiddleware(lambda request: None).process_request(request)
            MessageMiddleware(lambda request: None).process_request(request)
            send_magic_link(request, user, next_url)

            token = default_token_generator.make_token(user)
            uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
            url = reverse("users:login_with_link", kwargs={"uidb64": uidb64, "token": token})
            query_params = urlencode({"next": clean_next_url(next_url)})
            login_link = f"{settings.COMMU_PROTOCOL}://{settings.COMMU_FQDN}{url}?{query_params}"

            payload_as_str = respx.calls[0].request.content.decode()
            payload = json.loads(payload_as_str)
            assert payload["params"]["login_link"] == login_link
            assert payload_as_str.replace(login_link, "LOGIN_LINK") == snapshot(name="send_magic_link_payload")

            # we want messages do not appear in the productive environment
            msgs = get_messages(request)
            assert len(msgs._queued_messages) == count_msg
            if msgs._queued_messages:
                assert str(msgs._queued_messages[0]) == f'<a href="{login_link}">{login_link}</a> sent to {user.email}'


class TestLoginView:
    @pytest.mark.parametrize("next_url", [None, "/", "/topics/", "http://www.unallowed_host.com"])
    def test_content(self, client, db, next_url, snapshot):
        url = reverse("users:login") + f"?next={next_url}" if next_url else reverse("users:login")
        response = client.get(url)
        assert response.status_code == 200
        content = parse_response_to_soup(response, selector="main")
        assert str(content) == snapshot(name="login_view_content")

    @override_settings(ENVIRONMENT=Environment.PROD)
    @pytest.mark.parametrize("next_url,expected", next_url_tuples)
    def test_post(
        self,
        client,
        db,
        fixed_user_token,
        next_url,
        expected,
        snapshot,
        mock_token_generator,
        mock_respx_post_to_sib_smtp_url,
    ):
        user, uidb64, token = fixed_user_token
        response = client.post(
            reverse("users:login"),
            data={"email": user.email, "next": next_url},
        )

        assert response.status_code == 200
        content = parse_response_to_soup(response, selector="main")
        assert str(content) == snapshot(name="login_view_content")

        payload_as_str = respx.calls[0].request.content.decode()
        assert validate_magiclink_payload(payload_as_str, uidb64, token, expected)

    @pytest.mark.parametrize("next_url,expected", next_url_tuples)
    def test_redirection_when_email_is_unknown(self, client, db, next_url, expected, mock_respx_post_to_sib_smtp_url):
        response = client.post(
            reverse("users:login"),
            data={"email": "john@travolta.es", "next": next_url},
        )
        assert response.status_code == 302
        assert response.url == reverse("users:create") + "?" + urlencode(
            {"email": "john@travolta.es", "next": expected}
        )

    @pytest.mark.parametrize("next_url,expected", next_url_tuples)
    def test_user_is_already_authenticated(self, client, db, next_url, expected):
        user = UserFactory()
        client.force_login(user)
        url = reverse("users:login") + f"?next={next_url}"
        response = client.get(url)
        assert response.status_code == 302
        assert response.url == expected


class TestCreateUserView:
    @override_settings(ENVIRONMENT=Environment.PROD)
    @pytest.mark.parametrize("next_url,expected", next_url_tuples)
    def test_post_new_email(
        self, client, db, next_url, expected, snapshot, mock_token_generator, mock_respx_post_to_sib_smtp_url
    ):
        email = "john@travolta.lt"
        response = client.post(
            reverse("users:create"),
            data={"email": email, "first_name": "John", "last_name": "Travolta", "next": next_url},
        )
        assert response.status_code == 200

        content = parse_response_to_soup(response, selector="main")
        assert str(content) == snapshot(name="create_user_view_content")

        created_user = User.objects.get(email=email)
        pattern = r"^[a-f0-9]{8}(-[a-f0-9]{4}){3}-[a-f0-9]{12}$"
        assert re.match(pattern, created_user.username)
        assert created_user.email == email
        assert created_user.first_name == "John"
        assert created_user.last_name == "Travolta"
        assert created_user.identity_provider == IdentityProvider.MAGIC_LINK
        created_forum_profile = ForumProfile.objects.get(user=created_user)
        assert created_forum_profile.user.email == email

        _, uidb64, token = custom_user_token(created_user, fixed_token=True)
        payload_as_str = respx.calls[0].request.content.decode()
        assert validate_magiclink_payload(payload_as_str, uidb64, token, expected)

    @override_settings(ENVIRONMENT=Environment.PROD)
    @pytest.mark.parametrize("next_url,expected", next_url_tuples)
    def test_post_existing_email(
        self, client, db, user, next_url, expected, snapshot, mock_token_generator, mock_respx_post_to_sib_smtp_url
    ):
        first_name = user.first_name
        last_name = user.last_name
        response = client.post(
            reverse("users:create"),
            data={"email": user.email, "first_name": "Adam", "last_name": "Smith", "next": next_url},
        )
        assert response.status_code == 200
        content = parse_response_to_soup(response, selector="main")
        assert str(content) == snapshot(name="create_user_view_content")

        user.refresh_from_db()
        assert user.first_name == first_name
        assert user.last_name == last_name
        assert user.identity_provider == IdentityProvider.PRO_CONNECT

        _, uidb64, token = custom_user_token(user, fixed_token=True)
        payload_as_str = respx.calls[0].request.content.decode()
        assert validate_magiclink_payload(payload_as_str, uidb64, token, expected)


class TestLoginWithLinkView:
    def test_user_not_found(self, client, db):
        response = client.get(
            reverse("users:login_with_link", kwargs={"uidb64": "dGVzdEB0ZXN0LmNvbQ==", "token": "token"})
        )
        assert response.status_code == 302
        assert response.url == reverse("users:login")

    def test_invalid_token(self, client, db, user_token):
        _, uidb64, __doc__ = user_token
        response = client.get(reverse("users:login_with_link", kwargs={"uidb64": uidb64, "token": "invalid_token"}))
        assert response.status_code == 302
        assert response.url == reverse("users:login")

    def test_expired_token(self, client, db, user_token):
        user, uidb64, token = user_token

        client.force_login(user)
        # force logout
        client.session.flush()

        response = client.get(reverse("users:login_with_link", kwargs={"uidb64": uidb64, "token": token}))
        assert response.status_code == 302
        assert response.url == reverse("users:login")

    def test_success(self, client, db, user_token):
        _, uidb64, token = user_token
        next_url = "/topics/"

        response = client.get(
            reverse("users:login_with_link", kwargs={"uidb64": uidb64, "token": token}), data={"next": next_url}
        )
        assert response.status_code == 302
        assert response.url == next_url
        assert client.session.get(IdentityProvider.MAGIC_LINK.name) == 1

    def test_unallowed_next_url(self, client, db, user_token):
        _, uidb64, token = user_token
        next_url = "http://www.unallowed_host.com"

        response = client.get(
            reverse("users:login_with_link", kwargs={"uidb64": uidb64, "token": token}), data={"next": next_url}
        )
        assert response.status_code == 302
        assert response.url == "/"


class TestLogoutView:
    @pytest.mark.parametrize(
        "login,expected_logout_url",
        [("proconnect", reverse("openid_connect:logout")), ("magiclink", reverse("users:logout"))],
    )
    def test_logout_url_in_template(self, client, db, login, expected_logout_url):
        user = UserFactory()
        client.force_login(user)

        if login == "magiclink":
            session = client.session
            session[IdentityProvider.MAGIC_LINK.name] = 1
            session.save()

        response = client.get(reverse("pages:home"))
        assertContains(response, expected_logout_url)

    def test_logout_from_magiclink_session(self, client, db):
        user = UserFactory()
        client.force_login(user)
        response = client.get(reverse("users:logout"))
        assert response.status_code == 302
        assert response.url == reverse("pages:home")
        assert client.session.get("_auth_user_id") is None
        assert client.session.get("_auth_user_backend") is None
