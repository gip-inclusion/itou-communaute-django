# Generated by Django 4.2.8 on 2023-12-19 08:08

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("forum_conversation", "0007_certifiedpost"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="topic",
            name="likers",
        ),
    ]
