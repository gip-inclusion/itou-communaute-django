# Generated by Django 4.2.3 on 2023-09-04 10:45
import django.db.models.deletion
import storages.backends.s3boto3
from django.conf import settings
from django.db import migrations, models

import lacommunaute.forum_file.models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="PublicFile",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created", models.DateTimeField(auto_now_add=True, verbose_name="Creation date")),
                ("updated", models.DateTimeField(auto_now=True, verbose_name="Update date")),
                (
                    "file",
                    models.ImageField(
                        storage=storages.backends.s3.S3Storage(
                            bucket_name="set-bucket-name-public", default_acl="public-read", file_overwrite=False
                        ),
                        upload_to="",
                        validators=[lacommunaute.forum_file.models.validate_image_size],
                    ),
                ),
                ("keywords", models.CharField(max_length=255)),
                ("user", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                "verbose_name": "fichier public",
                "verbose_name_plural": "fichiers publics",
            },
        ),
    ]
