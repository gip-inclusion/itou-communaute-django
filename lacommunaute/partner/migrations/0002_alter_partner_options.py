# Generated by Django 5.0.8 on 2024-09-04 14:01

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("partner", "0001_initial"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="partner",
            options={"ordering": ["-updated"], "verbose_name": "Partner", "verbose_name_plural": "Partners"},
        ),
    ]
