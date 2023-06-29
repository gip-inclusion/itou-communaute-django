# Generated by Django 4.1.4 on 2022-12-28 07:15

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("forum_conversation", "0005_remove_post_upvoters"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="UpVote",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True, db_index=True, verbose_name="Creation date")),
                (
                    "post",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="upvotes",
                        to="forum_conversation.post",
                        verbose_name="Post",
                    ),
                ),
                (
                    "voter",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="upvotes",
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="Voter",
                    ),
                ),
            ],
            options={
                "ordering": ["-created_at"],
                "unique_together": {("voter", "post")},
            },
        ),
    ]
