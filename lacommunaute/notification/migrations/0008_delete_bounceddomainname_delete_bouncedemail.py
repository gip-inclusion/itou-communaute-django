# Generated by Django 5.0.1 on 2024-02-13 14:50

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("notification", "0007_bounceddomainname"),
        ("forum_moderation", "0002_copy_data_from_BouncedEmail_to_BlockedEmail"),
    ]

    operations = [
        migrations.DeleteModel(
            name="BouncedDomainName",
        ),
        migrations.DeleteModel(
            name="BouncedEmail",
        ),
    ]
