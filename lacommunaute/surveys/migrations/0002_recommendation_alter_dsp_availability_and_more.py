from django.db import migrations, models

from lacommunaute.surveys import enums


class Migration(migrations.Migration):
    dependencies = [
        ("surveys", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="Recommendation",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("codename", models.CharField(editable=False, max_length=100, unique=True)),
                ("category", models.CharField(editable=False, max_length=100)),
                ("text", models.TextField()),
            ],
            options={},
        ),
        migrations.AlterField(
            model_name="dsp",
            name="availability",
            field=models.PositiveIntegerField(
                choices=enums.DSPAvailability.choices,
                verbose_name="disponibilité",
            ),
        ),
        migrations.AlterField(
            model_name="dsp",
            name="housing",
            field=models.PositiveIntegerField(
                choices=enums.DSPHousing.choices,
                verbose_name="logement",
            ),
        ),
        migrations.AlterField(
            model_name="dsp",
            name="judicial",
            field=models.PositiveIntegerField(
                choices=enums.DSPJudicial.choices,
                verbose_name="situation judiciaire",
            ),
        ),
        migrations.AlterField(
            model_name="dsp",
            name="language_skills",
            field=models.PositiveIntegerField(
                choices=enums.DSPLanguageSkills.choices,
                verbose_name="maîtrise de la langue française",
            ),
        ),
        migrations.AlterField(
            model_name="dsp",
            name="mobility",
            field=models.PositiveIntegerField(
                choices=enums.DSPMobility.choices,
                verbose_name="mobilité",
            ),
        ),
        migrations.RemoveField(
            model_name="dsp",
            name="recommendations",
        ),
        migrations.AlterField(
            model_name="dsp",
            name="resources",
            field=models.PositiveIntegerField(
                choices=enums.DSPResources.choices,
                verbose_name="ressources",
            ),
        ),
        migrations.AlterField(
            model_name="dsp",
            name="rights_access",
            field=models.PositiveIntegerField(
                choices=enums.DSPRightsAccess.choices,
                verbose_name="accès aux droits",
            ),
        ),
        migrations.AlterField(
            model_name="dsp",
            name="work_capacity",
            field=models.PositiveIntegerField(
                choices=enums.DSPWorkCapacity.choices,
                verbose_name="capacité à occuper un poste de travail",
            ),
        ),
        migrations.AddField(
            model_name="dsp",
            name="recommendations",
            field=models.ManyToManyField(to="surveys.recommendation"),
        ),
    ]
