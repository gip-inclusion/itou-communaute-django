# Generated by Django 4.2.8 on 2023-12-12 10:09

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("metabase", "0002_posttable"),
    ]

    operations = [
        migrations.AlterField(
            model_name="posttable",
            name="subject",
            field=models.CharField(max_length=255, verbose_name="Sujet"),
        ),
    ]