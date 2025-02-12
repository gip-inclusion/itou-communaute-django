from django.contrib.admin.sites import AdminSite

from lacommunaute.users.admin import EmailLastSeenAdmin
from lacommunaute.users.models import EmailLastSeen


def test_permissions_on_email_last_seen(db):
    email_last_seen_admin = EmailLastSeenAdmin(EmailLastSeen, AdminSite())
    assert not email_last_seen_admin.has_add_permission(None)
    assert not email_last_seen_admin.has_change_permission(None)
    assert not email_last_seen_admin.has_delete_permission(None)
