import dataclasses
from urllib.parse import unquote

from django.core import signing
from django.db import models
from django.utils import crypto, timezone

from lacommunaute.inclusion_connect.constants import OIDC_STATE_EXPIRATION
from lacommunaute.users.models import User


class OIDConnectQuerySet(models.QuerySet):
    def cleanup(self, at=None):
        at = at if at else timezone.now() - OIDC_STATE_EXPIRATION
        return self.filter(created_at__lte=at).delete()


class InclusionConnectState(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    # Length used in call to get_random_string()
    csrf = models.CharField(max_length=12, unique=True)

    objects = OIDConnectQuerySet.as_manager()

    @classmethod
    def create_signed_csrf_token(cls):
        """
        Create and sign a new CSRF token to protect requests to identity providers.
        """
        token = crypto.get_random_string(length=12)
        cls.objects.create(csrf=token)

        signer = signing.Signer()
        signed_token = signer.sign(token)
        return signed_token

    @classmethod
    def is_valid(cls, signed_csrf):
        if not signed_csrf:
            return False

        signer = signing.Signer()
        try:
            csrf = signer.unsign(unquote(signed_csrf))
        except signing.BadSignature:
            return False

        # Cleanup old states if any.
        cls.objects.cleanup()

        state = cls.objects.filter(csrf=csrf).first()
        if not state:
            return False

        # One-time use
        state.delete()

        return True


@dataclasses.dataclass
class OIDConnectUserData:
    """
    Transforms data provided by the /userinfo endpoint into a Django-like User object.
    Note that this matches OpenID minimal claims (profile and email).
    """

    email: str
    first_name: str
    last_name: str
    username: str

    def create_or_update_user(self):
        """
        Create or update a user managed by another identity provider.
         - If there is already a user with this username (user_info_dict["sub"])
           and from the same identity provider, we update and return it.
         - If there is already a user with the email, we return this user.
         - otherwise, we create a new user based on the data we received.
        """
        user_data_dict = dataclasses.asdict(self)
        user_data_dict = {key: value for key, value in user_data_dict.items() if value}
        try:
            user = User.objects.get(username=self.username)
            created = False
        except User.DoesNotExist:
            # User.objects.create_user does the following:
            # - set User.is_active to true,
            # - call User.set_unusable_password() if no password is given.
            # https://docs.djangoproject.com/fr/4.0/ref/contrib/auth/#django.contrib.auth.models.UserManager.create_user
            # NB: if we already have a user with the same username but with a different email and a different
            # provider the code will break here. We know it but since it's highly unlikely we just added a test
            # on this behaviour. No need to do a fancy bypass if it's never used.
            user = User.objects.create_user(**user_data_dict)
            created = True

        if not created:
            for key, value in user_data_dict.items():
                setattr(user, key, value)

        user.save()
        return user, created

    @staticmethod
    def user_info_mapping_dict(user_info: dict):
        """
        Map Django's User class attributes to the identity provider ones.
        Override this method to add or change attributes.
        See https://openid.net/specs/openid-connect-core-1_0.html#StandardClaims
        """
        return {
            "username": user_info["sub"],
            "first_name": user_info["given_name"],
            "last_name": user_info["family_name"],
            "email": user_info["email"],
        }

    @classmethod
    def from_user_info(cls, user_info: dict):
        return cls(**cls.user_info_mapping_dict(user_info))
