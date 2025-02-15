from urllib.parse import urlencode

import httpx
import jwt
import respx
from django.contrib import auth
from django.contrib.sessions.middleware import SessionMiddleware
from django.test import RequestFactory, TestCase, override_settings
from django.urls import reverse

from lacommunaute.openid_connect import constants
from lacommunaute.openid_connect.models import OpenID_State
from lacommunaute.openid_connect.views import OpenID_Session
from lacommunaute.users.factories import UserFactory
from lacommunaute.users.models import User
from lacommunaute.utils.testing import reload_module


OIDC_USERINFO = {
    "given_name": "Michel",
    "usual_name": "AUDIARD",
    "email": "michel@lestontons.fr",
    "sub": "af6b26f9-85cd-484e-beb9-bea5be13e30f",
}


@override_settings(
    OPENID_CONNECT_BASE_URL="https://openid.connect.fake",
    OPENID_CONNECT_REALM="foobar",
    OPENID_CONNECT_CLIENT_ID="IC_CLIENT_ID_123",
    OPENID_CONNECT_CLIENT_SECRET="IC_CLIENT_SECRET_123",
)
@reload_module(constants)
class OpenID_BaseTestCase(TestCase):
    pass


# Make sure this decorator is before test definition, not here.
# @respx.mock
def mock_oauth_dance(
    test_class,
    previous_url=None,
    next_url=None,
    assert_redirects=True,
    expected_route="pages:home",
    user_info_email=None,
):
    respx.get(constants.OPENID_CONNECT_ENDPOINT_AUTHORIZE).respond(302)
    authorize_params = {
        "previous_url": previous_url,
        "next": next_url,
    }
    authorize_params = {k: v for k, v in authorize_params.items() if v}

    # Calling this view is mandatory to start a new session.
    authorize_url = f"{reverse('openid_connect:authorize')}?{urlencode(authorize_params)}"
    test_class.client.get(authorize_url)

    # User is logged out from IC when an error happens during the oauth dance.
    respx.get(constants.OPENID_CONNECT_ENDPOINT_LOGOUT).respond(200)

    token_json = {
        "access_token": "7890123",
        "token_type": "Bearer",
        "expires_in": 60,
        "id_token": "123456",
    }
    respx.post(constants.OPENID_CONNECT_ENDPOINT_TOKEN).mock(return_value=httpx.Response(200, json=token_json))

    user_info = OIDC_USERINFO.copy()
    if user_info_email:
        user_info["email"] = user_info_email
    user_info = user_info | {"aud": constants.OPENID_CONNECT_CLIENT_ID}
    user_info_jwt = jwt.encode(payload=user_info, key=constants.OPENID_CONNECT_CLIENT_SECRET, algorithm="HS256")
    respx.get(constants.OPENID_CONNECT_ENDPOINT_USERINFO).mock(return_value=httpx.Response(200, content=user_info_jwt))

    csrf_signed = OpenID_State.create_signed_csrf_token()
    url = reverse("openid_connect:callback")
    response = test_class.client.get(url, data={"code": "123", "state": csrf_signed})
    if assert_redirects:
        test_class.assertRedirects(response, reverse(expected_route))

    return response


class OpenID_ViewTest(OpenID_BaseTestCase):
    def test_callback_invalid_state(self):
        url = reverse("openid_connect:callback")
        response = self.client.get(url, data={"code": "123", "state": "000"})
        self.assertEqual(response.status_code, 302)

    def test_callback_no_state(self):
        url = reverse("openid_connect:callback")
        response = self.client.get(url, data={"code": "123"})
        self.assertEqual(response.status_code, 302)

    def test_callback_no_code(self):
        url = reverse("openid_connect:callback")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)

    def test_authorize_endpoint(self):
        url = f"{reverse('openid_connect:authorize')}"
        # Don't use assertRedirects to avoid fetching the last URL.
        response = self.client.get(url, follow=False)
        self.assertTrue(response.url.startswith(constants.OPENID_CONNECT_ENDPOINT_AUTHORIZE))
        self.assertIn(constants.OPENID_CONNECT_SESSION_KEY, self.client.session)

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
        self.assertEqual(user.last_name, OIDC_USERINFO["usual_name"])
        self.assertEqual(user.username, OIDC_USERINFO["sub"])

    @respx.mock
    def test_callback_existing_user(self):
        # User already exists.
        UserFactory(
            first_name=OIDC_USERINFO["given_name"],
            last_name=OIDC_USERINFO["usual_name"],
            username=OIDC_USERINFO["sub"],
            email=OIDC_USERINFO["email"],
        )
        mock_oauth_dance(self)
        self.assertEqual(User.objects.count(), 1)
        user = User.objects.get(email=OIDC_USERINFO["email"])
        self.assertEqual(user.first_name, OIDC_USERINFO["given_name"])
        self.assertEqual(user.last_name, OIDC_USERINFO["usual_name"])
        self.assertEqual(user.username, OIDC_USERINFO["sub"])


class OpenID_SessionTest(OpenID_BaseTestCase):
    def test_start_session(self):
        proc_session = OpenID_Session()
        self.assertEqual(proc_session.key, constants.OPENID_CONNECT_SESSION_KEY)

        expected_keys = [
            "token",
            "state",
            "previous_url",
            "next_url",
            "user_email",
            "request",
        ]
        proc_session_dict = proc_session.asdict()
        for key in expected_keys:
            with self.subTest(key):
                self.assertIn(key, proc_session_dict.keys())
                self.assertEqual(proc_session_dict[key], None)

        request = RequestFactory().get("/")
        middleware = SessionMiddleware(lambda x: x)
        middleware.process_request(request)
        request.session.save()
        request = proc_session.bind_to_request(request=request)
        self.assertTrue(request.session.get(constants.OPENID_CONNECT_SESSION_KEY))


class OpenID_LoginTest(OpenID_BaseTestCase):
    @respx.mock
    def test_normal_signin(self):
        """
        A user has created an account with Pro Connect.
        He logs out.
        He can log in again later.
        """
        # Create an account with IC.
        mock_oauth_dance(self)

        # Then log out.
        response = self.client.post(reverse("openid_connect:logout"))

        # Then log in again.
        response = self.client.get(reverse("pages:home"))
        self.assertContains(response, reverse("users:login"))

        response = mock_oauth_dance(self, assert_redirects=False)
        expected_redirection = reverse("pages:home")
        self.assertRedirects(response, expected_redirection)

        # Make sure it was a login instead of a new signup.
        users_count = User.objects.filter(email=OIDC_USERINFO["email"]).count()
        self.assertEqual(users_count, 1)


class OpenID_LogoutTest(OpenID_BaseTestCase):
    @respx.mock
    def test_logout_with_redirection(self):
        mock_oauth_dance(self)
        params = {
            "id_token_hint": 123456,
            "post_logout_redirect_uri": f'http://testserver{reverse("pages:home")}',
        }
        expected_redirection = f"{constants.OPENID_CONNECT_ENDPOINT_LOGOUT}?{urlencode(params)}"
        respx.get(constants.OPENID_CONNECT_ENDPOINT_LOGOUT).respond(200)
        logout_url = reverse("openid_connect:logout")
        response = self.client.get(logout_url)
        self.assertFalse(auth.get_user(self.client).is_authenticated)
        self.assertRedirects(response, expected_redirection, fetch_redirect_response=False)
