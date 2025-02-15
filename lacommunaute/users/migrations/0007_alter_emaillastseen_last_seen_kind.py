# Generated by Django 5.1.5 on 2025-02-11 09:43

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("users", "0006_emaillastseen"),
    ]

    operations = [
        migrations.AlterField(
            model_name="emaillastseen",
            name="last_seen_kind",
            field=models.CharField(
                choices=[
                    ("POST", "message"),
                    ("LOGGED", "connexion"),
                    ("VISITED", "notification cliquée"),
                ],
                max_length=12,
                verbose_name="last seen kind",
            ),
        ),
    ]
