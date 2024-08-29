from unittest import mock

from django.test import TestCase, override_settings
from django.utils import timezone

from lacommunaute.forum_member.models import ForumProfile
from lacommunaute.openid_connect import constants
from lacommunaute.openid_connect.models import OIDConnectUserData, OpenID_State
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


class OpenID_ModelTest(OpenID_BaseTestCase):
    def test_state_is_valid(self):
        csrf_signed = OpenID_State.create_signed_csrf_token()
        self.assertTrue(isinstance(csrf_signed, str))
        self.assertTrue(OpenID_State.is_valid(csrf_signed))

    def test_state_delete(self):
        state = OpenID_State.objects.create(csrf="foo")

        OpenID_State.objects.cleanup()

        state.refresh_from_db()
        self.assertIsNotNone(state)

        state.created_at = timezone.now() - constants.OIDC_STATE_EXPIRATION * 2
        state.save()

        OpenID_State.objects.cleanup()

        with self.assertRaises(OpenID_State.DoesNotExist):
            state.refresh_from_db()

    def test_create_user_from_user_info(self):
        """
        Nominal scenario: there is no user with OpenID_ email
        that is sent, so we create one.
        """
        proc_user_data = OIDConnectUserData.from_user_info(OIDC_USERINFO)
        self.assertFalse(User.objects.filter(username=proc_user_data.username).exists())
        self.assertFalse(User.objects.filter(email=proc_user_data.email).exists())

        now = timezone.now()
        with mock.patch("django.utils.timezone.now", return_value=now):
            user, created = proc_user_data.create_or_update_user()
        self.assertTrue(created)
        self.assertEqual(user.email, OIDC_USERINFO["email"])
        self.assertEqual(user.last_name, OIDC_USERINFO["usual_name"])
        self.assertEqual(user.first_name, OIDC_USERINFO["given_name"])
        self.assertEqual(user.username, OIDC_USERINFO["sub"])

        self.assertEqual(ForumProfile.objects.get(user=user).user, user)

    def test_update_user_from_user_info(self):
        USERINFO = {
            "first_name": "Jeff",
            "last_name": "BUCKLEY",
            "email": "jeff@buckley.com",
            "username": "af6b26f9-85cd-484e-beb9-bea5be13e30f",
        }
        user = UserFactory(**(USERINFO))
        ForumProfile.objects.create(user=user)

        proc_user_data = OIDConnectUserData.from_user_info(OIDC_USERINFO)

        now = timezone.now()
        with mock.patch("django.utils.timezone.now", return_value=now):
            _, created = proc_user_data.create_or_update_user()

        self.assertFalse(created)

        user = User.objects.get(username=USERINFO["username"])
        self.assertEqual(user.first_name, OIDC_USERINFO["given_name"])
        self.assertEqual(user.last_name, OIDC_USERINFO["usual_name"])
        self.assertEqual(user.email, OIDC_USERINFO["email"])
        self.assertNotEqual(user.email, USERINFO["email"])

        self.assertEqual(1, User.objects.count())
        self.assertTrue(ForumProfile.objects.get(user=user))

    def test_get_existing_user_with_existing_email(self):
        """
        If there already is an existing django user with email OpenID_ sent us, we do not create it again,
        We user it and we update it with the data form the identity_provider.
        """
        proc_user_data = OIDConnectUserData.from_user_info(OIDC_USERINFO)
        UserFactory(
            first_name=proc_user_data.first_name,
            last_name=proc_user_data.last_name,
            email=proc_user_data.email,
            username=proc_user_data.username,
        )
        user, created = proc_user_data.create_or_update_user()
        self.assertFalse(created)
        self.assertEqual(user.last_name, OIDC_USERINFO["usual_name"])
        self.assertEqual(user.first_name, OIDC_USERINFO["given_name"])
        self.assertEqual(user.username, OIDC_USERINFO["sub"])
