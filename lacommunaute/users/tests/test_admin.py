from django.contrib.admin.sites import AdminSite

from lacommunaute.users.admin import EmailLastSeenAdmin
from lacommunaute.users.models import EmailLastSeen


def test_email_hash_readonly_field(db):
    form = EmailLastSeenAdmin(EmailLastSeen, AdminSite()).get_form(request=None)
    for field in ["email", "email_hash", "deleted_at"]:
        assert field not in form.base_fields
