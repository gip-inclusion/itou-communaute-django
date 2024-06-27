import pytest
from django.db import connection


@pytest.fixture(name="reset_model_sequence")
def reset_model_sequence_fixture(request, db):
    """
    :return: a function which can adjust and reset a primary key sequence for use as a pytest fixture
    it is used to temporarily change the primary key, so that it is predictable (e.g. for snapshots)
    """
    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT setval(pg_get_serial_sequence(%s, 'id'), %s, false);", (request.param._meta.db_table, "9999")
        )
