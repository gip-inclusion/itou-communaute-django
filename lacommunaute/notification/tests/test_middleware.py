import pytest

from lacommunaute.notification.factories import NotificationFactory
from lacommunaute.notification.models import Notification
from lacommunaute.users.models import EmailLastSeen


@pytest.mark.parametrize(
    "notif_param, expected_visited_at",
    [
        ("", None),
        ("malformed", None),
        ("74eb2ba8-04bf-489f-8c1d-fd1b34b0f3e9", None),
        (lambda: str(NotificationFactory().uuid), True),
    ],
)
def test_notif_param(client, db, notif_param, expected_visited_at):
    misc_notification = NotificationFactory()
    if callable(notif_param):
        notif_param = notif_param()

    client.get(f"/?notif={notif_param}")

    if expected_visited_at:
        notification = Notification.objects.get(uuid=notif_param)
        notification.refresh_from_db()
        assert notification.visited_at is not None

        email_last_seen = EmailLastSeen.objects.get()
        assert email_last_seen.email == notification.recipient

    misc_notification.refresh_from_db()
    assert misc_notification.visited_at is None
