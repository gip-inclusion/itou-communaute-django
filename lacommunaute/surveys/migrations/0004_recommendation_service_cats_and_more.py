# Generated by Django 5.0.3 on 2024-03-11 17:07

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("surveys", "0003_dsp_city_code_dsp_latitude_dsp_location_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="recommendation",
            name="dora_cats",
            field=models.JSONField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="recommendation",
            name="dora_subs",
            field=models.JSONField(blank=True, null=True),
        ),
    ]
