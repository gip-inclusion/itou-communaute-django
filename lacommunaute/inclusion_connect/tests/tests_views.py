from urllib.parse import urlencode

import httpx
import respx
from django.contrib import auth
from django.contrib.sessions.middleware import SessionMiddleware
from django.test import RequestFactory, TestCase, override_settings
from django.urls import reverse

from lacommunaute.inclusion_connect import constants
from lacommunaute.inclusion_connect.models import InclusionConnectState
from lacommunaute.inclusion_connect.views import InclusionConnectSession
from lacommunaute.users.factories import UserFactory
from lacommunaute.users.models import User
from lacommunaute.utils.testing import reload_module


OIDC_USERINFO = {
    "given_name": "Michel",
    "family_name": "AUDIARD",
    "email": "michel@lestontons.fr",
    "sub": "af6b26f9-85cd-484e-beb9-bea5be13e30f",
}


@override_settings(
    INCLUSION_CONNECT_BASE_URL="https://inclusion.connect.fake",
    INCLUSION_CONNECT_REALM="foobar",
    INCLUSION_CONNECT_CLIENT_ID="IC_CLIENT_ID_123",
    INCLUSION_CONNECT_CLIENT_SECRET="IC_CLIENT_SECRET_123",
)
@reload_module(constants)
class InclusionConnectBaseTestCase(TestCase):
    pass


# Make sure this decorator is before test definition, not here.
# @respx.mock
def mock_oauth_dance(
    test_class,
    previous_url=None,
    next_url=None,
    assert_redirects=True,
    expected_route="forum_extension:home",
    user_info_email=None,
):
    respx.get(constants.INCLUSION_CONNECT_ENDPOINT_AUTHORIZE).respond(302)
    authorize_params = {
        "previous_url": previous_url,
        "next_url": next_url,
    }
    authorize_params = {k: v for k, v in authorize_params.items() if v}

    # Calling this view is mandatory to start a new session.
    authorize_url = f"{reverse('inclusion_connect:authorize')}?{urlencode(authorize_params)}"
    test_class.client.get(authorize_url)

    # User is logged out from IC when an error happens during the oauth dance.
    respx.get(constants.INCLUSION_CONNECT_ENDPOINT_LOGOUT).respond(200)

    token_json = {
        "access_token": "7890123",
        "token_type": "Bearer",
        "expires_in": 60,
        "id_token": "123456",
    }
    respx.post(constants.INCLUSION_CONNECT_ENDPOINT_TOKEN).mock(return_value=httpx.Response(200, json=token_json))

    user_info = OIDC_USERINFO.copy()
    if user_info_email:
        user_info["email"] = user_info_email
    respx.get(constants.INCLUSION_CONNECT_ENDPOINT_USERINFO).mock(return_value=httpx.Response(200, json=user_info))

    csrf_signed = InclusionConnectState.create_signed_csrf_token()
    url = reverse("inclusion_connect:callback")
    response = test_class.client.get(url, data={"code": "123", "state": csrf_signed})
    if assert_redirects:
        test_class.assertRedirects(response, reverse(expected_route))

    return response


class InclusionConnectViewTest(InclusionConnectBaseTestCase):
    def test_callback_invalid_state(self):
        url = reverse("inclusion_connect:callback")
        response = self.client.get(url, data={"code": "123", "state": "000"})
        self.assertEqual(response.status_code, 302)

    def test_callback_no_state(self):
        url = reverse("inclusion_connect:callback")
        response = self.client.get(url, data={"code": "123"})
        self.assertEqual(response.status_code, 302)

    def test_callback_no_code(self):
        url = reverse("inclusion_connect:callback")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)

    def test_authorize_endpoint(self):
        url = f"{reverse('inclusion_connect:authorize')}"
        # Don't use assertRedirects to avoid fetching the last URL.
        response = self.client.get(url, follow=False)
        self.assertTrue(response.url.startswith(constants.INCLUSION_CONNECT_ENDPOINT_AUTHORIZE))
        self.assertIn(constants.INCLUSION_CONNECT_SESSION_KEY, self.client.session)

    ####################################
    ######### Callback tests ###########
    ####################################
    @respx.mock
    def test_callback_user_created(self):
        ### User does not exist.
        mock_oauth_dance(self)
        self.assertEqual(User.objects.count(), 1)
        user = User.objects.get(email=OIDC_USERINFO["email"])
        self.assertEqual(user.first_name, OIDC_USERINFO["given_name"])
        self.assertEqual(user.last_name, OIDC_USERINFO["family_name"])
        self.assertEqual(user.username, OIDC_USERINFO["sub"])

    @respx.mock
    def test_callback_existing_user(self):
        # User already exists.
        UserFactory(
            first_name=OIDC_USERINFO["given_name"],
            last_name=OIDC_USERINFO["family_name"],
            username=OIDC_USERINFO["sub"],
            email=OIDC_USERINFO["email"],
        )
        mock_oauth_dance(self)
        self.assertEqual(User.objects.count(), 1)
        user = User.objects.get(email=OIDC_USERINFO["email"])
        self.assertEqual(user.first_name, OIDC_USERINFO["given_name"])
        self.assertEqual(user.last_name, OIDC_USERINFO["family_name"])
        self.assertEqual(user.username, OIDC_USERINFO["sub"])


class InclusionConnectSessionTest(InclusionConnectBaseTestCase):
    def test_start_session(self):
        ic_session = InclusionConnectSession()
        self.assertEqual(ic_session.key, constants.INCLUSION_CONNECT_SESSION_KEY)

        expected_keys = [
            "token",
            "state",
            "previous_url",
            "next_url",
            "user_email",
            "request",
        ]
        ic_session_dict = ic_session.asdict()
        for key in expected_keys:
            with self.subTest(key):
                self.assertIn(key, ic_session_dict.keys())
                self.assertEqual(ic_session_dict[key], None)

        request = RequestFactory().get("/")
        middleware = SessionMiddleware(lambda x: x)
        middleware.process_request(request)
        request.session.save()
        request = ic_session.bind_to_request(request=request)
        self.assertTrue(request.session.get(constants.INCLUSION_CONNECT_SESSION_KEY))


class InclusionConnectLoginTest(InclusionConnectBaseTestCase):
    @respx.mock
    def test_normal_signin(self):
        """
        A user has created an account with Inclusion Connect.
        He logs out.
        He can log in again later.
        """
        # Create an account with IC.
        mock_oauth_dance(self)

        # Then log out.
        response = self.client.post(reverse("inclusion_connect:logout"))

        # Then log in again.
        response = self.client.get(reverse("forum_extension:home"))
        self.assertContains(response, reverse("inclusion_connect:authorize"))

        response = mock_oauth_dance(self, assert_redirects=False)
        expected_redirection = reverse("forum_extension:home")
        self.assertRedirects(response, expected_redirection)

        # Make sure it was a login instead of a new signup.
        users_count = User.objects.filter(email=OIDC_USERINFO["email"]).count()
        self.assertEqual(users_count, 1)

        self.assertIn("upper_visible_forums", response.wsgi_request.session.keys())


class InclusionConnectLogoutTest(InclusionConnectBaseTestCase):
    @respx.mock
    def test_simple_logout(self):
        mock_oauth_dance(self)
        respx.get(constants.INCLUSION_CONNECT_ENDPOINT_LOGOUT).respond(200)
        logout_url = reverse("inclusion_connect:logout")
        response = self.client.get(logout_url)
        self.assertRedirects(response, reverse("forum_extension:home"))
        self.assertFalse(auth.get_user(self.client).is_authenticated)

    @respx.mock
    def test_logout_with_redirection(self):
        mock_oauth_dance(self)
        expected_redirection = reverse("forum_extension:home")
        respx.get(constants.INCLUSION_CONNECT_ENDPOINT_LOGOUT).respond(200)

        params = {"redirect_url": expected_redirection}
        logout_url = f"{reverse('inclusion_connect:logout')}?{urlencode(params)}"
        response = self.client.get(logout_url)
        self.assertRedirects(response, expected_redirection)
