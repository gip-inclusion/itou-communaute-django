import pytest

from lacommunaute.users.enums import EmailLastSeenKind
from lacommunaute.users.factories import UserFactory
from lacommunaute.users.models import EmailLastSeen


@pytest.mark.parametrize("logged", [True, False])
def test_mark_as_seen_logged_user_middleware(client, db, logged):
    if logged:
        user = UserFactory()
        client.force_login(user)

    response = client.get("/")
    assert response.status_code == 200

    if logged:
        email_last_seen = EmailLastSeen.objects.get()
        assert email_last_seen.email == user.email
        assert email_last_seen.last_seen_kind == EmailLastSeenKind.LOGGED
    else:
        assert not EmailLastSeen.objects.exists()
