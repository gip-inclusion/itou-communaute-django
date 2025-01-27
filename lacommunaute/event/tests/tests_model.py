import pytest
from django.db import IntegrityError

from lacommunaute.event.factories import EventFactory
from lacommunaute.users.models import EmailLastSeen


class TestEventModel:
    def test_user_is_mandatory(self, db):
        with pytest.raises(IntegrityError):
            EventFactory(poster=None)

    def test_email_last_seen_updated_on_save(self, db):
        EventFactory()

        email_last_seen = EmailLastSeen.objects.get()
        assert email_last_seen.last_seen_kind == "EVENT"
