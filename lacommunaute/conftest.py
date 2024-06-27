import pytest
from django.db import connection


@pytest.fixture(name="reset_model_sequence")
def reset_model_sequence_fixture():
    """
    :return: a function which can adjust and reset a primary key sequence for use as a pytest fixture
    it is used to temporarily change the primary key, so that it is predictable (e.g. for snapshots)
    """

    def reset_model_sequence(*model_classes):
        with connection.cursor() as cursor:
            for model_class in model_classes:
                cursor.execute(
                    "SELECT setval(pg_get_serial_sequence(%s, 'id'), %s, false);", (model_class._meta.db_table, "9999")
                )

    return reset_model_sequence
