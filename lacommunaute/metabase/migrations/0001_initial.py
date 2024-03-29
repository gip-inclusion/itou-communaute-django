# Generated by Django 4.2.7 on 2023-12-05 15:56

from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="ForumTable",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=100, verbose_name="Nom")),
                (
                    "kind",
                    models.CharField(
                        choices=[
                            ("PUBLIC_FORUM", "Espace public"),
                            ("PRIVATE_FORUM", "Espace privé"),
                            ("NEWS", "Actualités"),
                        ],
                        default="PUBLIC_FORUM",
                        max_length=20,
                        verbose_name="Kind",
                    ),
                ),
                ("type", models.CharField(max_length=20, verbose_name="Type")),
                (
                    "short_description_boolean",
                    models.BooleanField(default=False, verbose_name="Présence d'une description courte"),
                ),
                ("description_boolean", models.BooleanField(default=False, verbose_name="Présence d'une description")),
                ("parent_name", models.CharField(max_length=100, null=True, verbose_name="Nom du forum parent")),
                (
                    "direct_topics_count",
                    models.PositiveIntegerField(default=0, verbose_name="Nombre de sujets directs"),
                ),
                ("upvotes_count", models.PositiveIntegerField(default=0, verbose_name="Nombre d'upvotes")),
                ("last_post_at", models.DateTimeField(null=True, verbose_name="Date du dernier message")),
                ("last_updated_at", models.DateTimeField(null=True, verbose_name="Date de dernière mise à jour")),
                (
                    "extracted_at",
                    models.DateTimeField(auto_now_add=True, verbose_name="Date d'extraction des données"),
                ),
            ],
            options={
                "verbose_name": "Forum Table",
                "verbose_name_plural": "Forums Table",
                "ordering": ["name"],
            },
        ),
    ]
