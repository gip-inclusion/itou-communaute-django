from unittest import mock

from django.test import TestCase, override_settings
from django.utils import timezone

from lacommunaute.forum_member.models import ForumProfile
from lacommunaute.inclusion_connect import constants
from lacommunaute.inclusion_connect.models import InclusionConnectState, OIDConnectUserData
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


class InclusionConnectModelTest(InclusionConnectBaseTestCase):
    def test_state_is_valid(self):
        csrf_signed = InclusionConnectState.create_signed_csrf_token()
        self.assertTrue(isinstance(csrf_signed, str))
        self.assertTrue(InclusionConnectState.is_valid(csrf_signed))

    def test_state_delete(self):
        state = InclusionConnectState.objects.create(csrf="foo")

        InclusionConnectState.objects.cleanup()

        state.refresh_from_db()
        self.assertIsNotNone(state)

        state.created_at = timezone.now() - constants.OIDC_STATE_EXPIRATION * 2
        state.save()

        InclusionConnectState.objects.cleanup()

        with self.assertRaises(InclusionConnectState.DoesNotExist):
            state.refresh_from_db()

    def test_create_user_from_user_info(self):
        """
        Nominal scenario: there is no user with InclusionConnect email
        that is sent, so we create one.
        """
        ic_user_data = OIDConnectUserData.from_user_info(OIDC_USERINFO)
        self.assertFalse(User.objects.filter(username=ic_user_data.username).exists())
        self.assertFalse(User.objects.filter(email=ic_user_data.email).exists())

        now = timezone.now()
        with mock.patch("django.utils.timezone.now", return_value=now):
            user, created = ic_user_data.create_or_update_user()
        self.assertTrue(created)
        self.assertEqual(user.email, OIDC_USERINFO["email"])
        self.assertEqual(user.last_name, OIDC_USERINFO["family_name"])
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

        ic_user_data = OIDConnectUserData.from_user_info(OIDC_USERINFO)

        now = timezone.now()
        with mock.patch("django.utils.timezone.now", return_value=now):
            _, created = ic_user_data.create_or_update_user()

        self.assertFalse(created)

        user = User.objects.get(username=USERINFO["username"])
        self.assertEqual(user.first_name, OIDC_USERINFO["given_name"])
        self.assertEqual(user.last_name, OIDC_USERINFO["family_name"])
        self.assertEqual(user.email, OIDC_USERINFO["email"])
        self.assertNotEqual(user.email, USERINFO["email"])

        self.assertEqual(1, User.objects.count())
        self.assertTrue(ForumProfile.objects.get(user=user))

    def test_get_existing_user_with_existing_email(self):
        """
        If there already is an existing django user with email InclusionConnect sent us, we do not create it again,
        We user it and we update it with the data form the identity_provider.
        """
        ic_user_data = OIDConnectUserData.from_user_info(OIDC_USERINFO)
        UserFactory(
            first_name=ic_user_data.first_name,
            last_name=ic_user_data.last_name,
            email=ic_user_data.email,
            username=ic_user_data.username,
        )
        user, created = ic_user_data.create_or_update_user()
        self.assertFalse(created)
        self.assertEqual(user.last_name, OIDC_USERINFO["family_name"])
        self.assertEqual(user.first_name, OIDC_USERINFO["given_name"])
        self.assertEqual(user.username, OIDC_USERINFO["sub"])
