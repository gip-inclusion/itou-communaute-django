# Generated by Django 4.2 on 2023-05-17 15:27

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("forum", "0008_alter_forum_members_group"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="forum",
            name="target_audience",
        ),
    ]
