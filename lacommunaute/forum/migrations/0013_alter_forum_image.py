# Generated by Django 5.0.6 on 2024-05-21 14:55

import storages.backends.s3
from django.conf import settings
from django.db import migrations, models

import lacommunaute.forum.models


class Migration(migrations.Migration):
    dependencies = [
        ("forum", "0012_forum_short_description_alter_forum_kind"),
    ]

    operations = [
        migrations.AlterField(
            model_name="forum",
            name="image",
            field=models.ImageField(
                storage=storages.backends.s3.S3Storage(
                    bucket_name=settings.AWS_STORAGE_BUCKET_NAME, file_overwrite=False
                ),
                upload_to="",
                validators=[lacommunaute.forum.models.validate_image_size],
            ),
        ),
    ]
