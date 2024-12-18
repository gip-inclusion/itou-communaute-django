import pytest
from django.core.management import call_command


@pytest.fixture(scope="session", autouse=True)
def run_compress(django_db_setup, django_db_blocker):
    with django_db_blocker.unblock():
        call_command("compress", "--force")
