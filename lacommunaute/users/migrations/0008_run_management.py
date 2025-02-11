# Generated by Django 5.1.5 on 2025-02-11 14:37

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("users", "0007_alter_emaillastseen_last_seen_kind"),
    ]

    operations = [
        migrations.RunSQL(
            """
            UPDATE users_user
            SET email = regexp_replace(email, '@pole-emploi.fr$', '@francetravail.fr')
            WHERE email LIKE '%@pole-emploi.fr';
            """
        ),
        migrations.RunSQL(
            """
            UPDATE users_emaillastseen
            SET email = regexp_replace(email, '@pole-emploi.fr$', '@francetravail.fr')
            WHERE email LIKE '%@pole-emploi.fr';
            """,
            elidable=True,
        ),
    ]
