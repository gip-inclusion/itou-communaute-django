# Generated by Django 4.1.2 on 2022-10-18 09:05

import django.db.models.deletion
import machina.core.validators
import machina.models.fields
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("forum", "0001_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Post",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "created",
                    models.DateTimeField(auto_now_add=True, verbose_name="Creation date"),
                ),
                (
                    "updated",
                    models.DateTimeField(auto_now=True, verbose_name="Update date"),
                ),
                (
                    "anonymous_key",
                    models.CharField(
                        blank=True,
                        max_length=100,
                        null=True,
                        verbose_name="Anonymous user forum key",
                    ),
                ),
                ("subject", models.CharField(max_length=255, verbose_name="Subject")),
                (
                    "content",
                    machina.models.fields.MarkupTextField(
                        no_rendered_field=True,
                        validators=[machina.core.validators.MarkupMaxLengthValidator(None)],
                        verbose_name="Content",
                    ),
                ),
                (
                    "username",
                    models.CharField(blank=True, max_length=155, null=True, verbose_name="Username"),
                ),
                (
                    "approved",
                    models.BooleanField(db_index=True, default=True, verbose_name="Approved"),
                ),
                (
                    "enable_signature",
                    models.BooleanField(db_index=True, default=True, verbose_name="Attach a signature"),
                ),
                (
                    "update_reason",
                    models.CharField(
                        blank=True,
                        max_length=255,
                        null=True,
                        verbose_name="Update reason",
                    ),
                ),
                (
                    "updates_count",
                    models.PositiveIntegerField(
                        blank=True,
                        default=0,
                        editable=False,
                        verbose_name="Updates count",
                    ),
                ),
                (
                    "_content_rendered",
                    models.TextField(blank=True, editable=False, null=True),
                ),
                (
                    "poster",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="posts",
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="Poster",
                    ),
                ),
            ],
            options={
                "verbose_name": "Post",
                "verbose_name_plural": "Posts",
                "ordering": ["created"],
                "get_latest_by": "created",
                "abstract": False,
            },
        ),
        migrations.CreateModel(
            name="Topic",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("subject", models.CharField(max_length=255, verbose_name="Subject")),
                ("slug", models.SlugField(max_length=255, verbose_name="Slug")),
                (
                    "type",
                    models.PositiveSmallIntegerField(
                        choices=[(0, "Default topic"), (1, "Sticky"), (2, "Announce")],
                        db_index=True,
                        verbose_name="Topic type",
                    ),
                ),
                (
                    "status",
                    models.PositiveIntegerField(
                        choices=[
                            (0, "Topic unlocked"),
                            (1, "Topic locked"),
                            (2, "Topic moved"),
                        ],
                        db_index=True,
                        verbose_name="Topic status",
                    ),
                ),
                (
                    "approved",
                    models.BooleanField(db_index=True, default=True, verbose_name="Approved"),
                ),
                (
                    "posts_count",
                    models.PositiveIntegerField(
                        blank=True,
                        default=0,
                        editable=False,
                        verbose_name="Posts count",
                    ),
                ),
                (
                    "views_count",
                    models.PositiveIntegerField(
                        blank=True,
                        default=0,
                        editable=False,
                        verbose_name="Views count",
                    ),
                ),
                (
                    "last_post_on",
                    models.DateTimeField(
                        blank=True,
                        db_index=True,
                        null=True,
                        verbose_name="Last post added on",
                    ),
                ),
                (
                    "created",
                    models.DateTimeField(auto_now_add=True, db_index=True, verbose_name="Creation date"),
                ),
                (
                    "updated",
                    models.DateTimeField(auto_now=True, db_index=True, verbose_name="Update date"),
                ),
                (
                    "first_post",
                    models.ForeignKey(
                        blank=True,
                        editable=False,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="+",
                        to="forum_conversation.post",
                        verbose_name="First post",
                    ),
                ),
                (
                    "forum",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="topics",
                        to="forum.forum",
                        verbose_name="Topic forum",
                    ),
                ),
                (
                    "last_post",
                    models.ForeignKey(
                        blank=True,
                        editable=False,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="+",
                        to="forum_conversation.post",
                        verbose_name="Last post",
                    ),
                ),
                (
                    "poster",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="Poster",
                    ),
                ),
                (
                    "subscribers",
                    models.ManyToManyField(
                        blank=True,
                        related_name="topic_subscriptions",
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="Subscribers",
                    ),
                ),
            ],
            options={
                "verbose_name": "Topic",
                "verbose_name_plural": "Topics",
                "ordering": ["-type", "-last_post_on"],
                "get_latest_by": "last_post_on",
                "abstract": False,
            },
        ),
        migrations.AddField(
            model_name="post",
            name="topic",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="posts",
                to="forum_conversation.topic",
                verbose_name="Topic",
            ),
        ),
        migrations.AddField(
            model_name="post",
            name="updated_by",
            field=models.ForeignKey(
                blank=True,
                editable=False,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to=settings.AUTH_USER_MODEL,
                verbose_name="Lastly updated by",
            ),
        ),
        migrations.AddIndex(
            model_name="topic",
            index=models.Index(fields=["type", "last_post_on"], name="forum_conve_type_cc96d0_idx"),
        ),
    ]
