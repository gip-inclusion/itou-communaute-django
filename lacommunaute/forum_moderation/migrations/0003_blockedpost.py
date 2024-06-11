# Generated by Django 5.0.6 on 2024-06-07 10:09

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("forum_moderation", "0002_copy_data_from_BouncedEmail_to_BlockedEmail"),
    ]

    operations = [
        migrations.CreateModel(
            name="BlockedPost",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created", models.DateTimeField(auto_now_add=True, verbose_name="Creation date")),
                ("updated", models.DateTimeField(auto_now=True, verbose_name="Update date")),
                (
                    "poster",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=models.deletion.CASCADE,
                        related_name="blocked_posts",
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="Poster",
                    ),
                ),
                ("username", models.EmailField(max_length=254, verbose_name="Adresse email")),
                ("content", models.CharField(verbose_name="Content")),
                ("block_reason", models.CharField(verbose_name="Block Reason")),
            ],
            options={
                "verbose_name": "Blocked Post",
                "verbose_name_plural": "Blocked Posts",
            },
        ),
    ]
