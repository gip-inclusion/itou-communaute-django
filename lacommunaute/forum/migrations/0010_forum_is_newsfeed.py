# Generated by Django 4.2 on 2023-05-22 09:55

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("forum", "0009_remove_forum_target_audience"),
    ]

    operations = [
        migrations.AddField(
            model_name="forum",
            name="is_newsfeed",
            field=models.BooleanField(default=False, verbose_name="fil d'actualité"),
        ),
    ]
