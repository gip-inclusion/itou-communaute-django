from django.db import models
from machina.models.abstract_models import DatedModel

from lacommunaute.users.models import User


class DSP(DatedModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="User")
    work_capacity = models.CharField(null=False, blank=False, max_length=1)
    language_skills = models.CharField(null=False, blank=False, max_length=1)
    housing = models.CharField(null=False, blank=False, max_length=1)
    rights_access = models.CharField(null=False, blank=False, max_length=1)
    mobility = models.CharField(null=False, blank=False, max_length=1)
    resources = models.CharField(null=False, blank=False, max_length=1)
    judicial = models.CharField(null=False, blank=False, max_length=1)
    availability = models.CharField(null=False, blank=False, max_length=1)
    recommendations = models.JSONField()

    class Meta:
        verbose_name = "Diagnostic socio-professionnel"
        verbose_name_plural = "Diagnostics socio-professionnels"
