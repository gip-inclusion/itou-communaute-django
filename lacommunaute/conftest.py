import pytest
from django.core.management import call_command

from lacommunaute.users.factories import UserFactory


@pytest.fixture(scope="session", autouse=True)
def run_compress(django_db_setup, django_db_blocker):
    with django_db_blocker.unblock():
        call_command("compress", "--force")


@pytest.fixture
def admin_client(client):
    client.force_login(UserFactory(is_in_staff_group=True, is_superuser=True))
    return client
