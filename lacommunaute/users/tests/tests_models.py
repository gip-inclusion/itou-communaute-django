import re

import pytest

from lacommunaute.users.enums import IdentityProvider
from lacommunaute.users.models import User


def test_create_user_without_username(db):
    user = User.objects.create_user(email="alex@honnold.com")
    assert re.match(r"^[a-f0-9]{8}(-[a-f0-9]{4}){3}-[a-f0-9]{12}$", user.username)
    assert user.email == "alex@honnold.com"


@pytest.mark.parametrize(
    "identity_provider,is_proconnect",
    [(provider.value, False) for provider in IdentityProvider if provider != IdentityProvider.PRO_CONNECT]
    + [(IdentityProvider.PRO_CONNECT.value, True)],
)
def test_is_proconnect(identity_provider, is_proconnect):
    user = User(identity_provider=identity_provider)
    assert user.is_proconnect() == is_proconnect
