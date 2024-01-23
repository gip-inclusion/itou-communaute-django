from django.db import models
from machina.models.abstract_models import DatedModel

from lacommunaute.surveys import enums
from lacommunaute.users.models import User


class Recommendation(models.Model):
    codename = models.CharField(editable=False, max_length=100, unique=True)
    category = models.CharField(editable=False, max_length=100)
    text = models.TextField()

    def __str__(self):
        return f"[{self.category}] {self.text}"


class DSP(DatedModel):
    CATEGORIES = [
        "work_capacity",
        "language_skills",
        "housing",
        "rights_access",
        "mobility",
        "resources",
        "judicial",
        "availability",
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="User")
    work_capacity = models.PositiveIntegerField(
        choices=enums.DSPWorkCapacity.choices,
        verbose_name="capacité à occuper un poste de travail",
    )
    language_skills = models.PositiveIntegerField(
        choices=enums.DSPLanguageSkills.choices,
        verbose_name="maîtrise de la langue française",
    )
    housing = models.PositiveIntegerField(
        choices=enums.DSPHousing.choices,
        verbose_name="logement",
    )
    rights_access = models.PositiveIntegerField(
        choices=enums.DSPRightsAccess.choices,
        verbose_name="accès aux droits",
    )
    mobility = models.PositiveIntegerField(
        choices=enums.DSPMobility.choices,
        verbose_name="mobilité",
    )
    resources = models.PositiveIntegerField(
        choices=enums.DSPResources.choices,
        verbose_name="ressources",
    )
    judicial = models.PositiveIntegerField(
        choices=enums.DSPJudicial.choices,
        verbose_name="situation judiciaire",
    )
    availability = models.PositiveIntegerField(
        choices=enums.DSPAvailability.choices,
        verbose_name="disponibilité",
    )
    recommendations = models.ManyToManyField(Recommendation)

    class Meta:
        verbose_name = "diagnostic socio-professionnel"
        verbose_name_plural = "diagnostics socio-professionnels"
