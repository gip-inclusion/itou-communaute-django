# Generated by Django 5.0.9 on 2024-11-25 15:15

from uuid import uuid4

from django.db import migrations
from django.db.models import F

from lacommunaute.users.models import User


def cleanup_email_in_username(apps, schema_editor):
    users_to_migrate = User.objects.filter(username=F("email"))

    while batch_users := users_to_migrate[:1000]:
        for user in batch_users:
            user.username = str(uuid4())
        User.objects.bulk_update(batch_users, ["username"])


class Migration(migrations.Migration):
    dependencies = [
        ("users", "0004_alter_user_managers"),
    ]

    operations = [
        migrations.RunPython(cleanup_email_in_username, migrations.RunPython.noop),
    ]

    elidable = True
