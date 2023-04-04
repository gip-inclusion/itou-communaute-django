# Generated by Django 4.1.7 on 2023-03-30 11:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("notification", "0002_emailsenttrack_kind"),
    ]

    operations = [
        migrations.AlterField(
            model_name="emailsenttrack",
            name="kind",
            field=models.CharField(
                choices=[
                    ("first_reply", "Première réponse à un sujet"),
                    ("onboarding", "Onboarding d'un nouvel utilisateur"),
                    ("pending_topic", "Question sans réponse"),
                ],
                max_length=15,
                verbose_name="Type",
            ),
        ),
    ]
