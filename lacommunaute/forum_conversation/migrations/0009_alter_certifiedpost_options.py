# Generated by Django 5.0.6 on 2024-06-07 10:34

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("forum_conversation", "0008_remove_topic_likers"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="certifiedpost",
            options={
                "ordering": ["-created"],
                "verbose_name": "Certified Post",
                "verbose_name_plural": "Certified Posts",
            },
        ),
    ]