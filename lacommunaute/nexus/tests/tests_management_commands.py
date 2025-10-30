from django.core.management import call_command
from django.utils import timezone
from freezegun import freeze_time

from lacommunaute.nexus.management.commands.populate_metabase_nexus import create_table, get_connection
from lacommunaute.users.factories import UserFactory


@freeze_time()
def test_populate_metabase_nexus(db):
    user = UserFactory()

    create_table()
    call_command("populate_metabase_nexus")

    with get_connection() as conn, conn.cursor() as cursor:
        cursor.execute("SELECT * FROM users")
        rows = cursor.fetchall()
        assert rows == [
            (
                "la-communauté",
                str(user.pk),
                f"la-communauté--{user.pk}",
                user.last_name,
                user.first_name,
                user.email,
                "",
                user.last_login,
                user.get_identity_provider_display(),
                "N/A",
                timezone.now(),
            ),
        ]
