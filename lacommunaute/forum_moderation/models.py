from django.db import models
from machina.models.abstract_models import DatedModel


class BlockedEmail(DatedModel):
    email = models.EmailField(verbose_name="email", null=False, blank=False, unique=True)
    reason = models.CharField(verbose_name="raison", max_length=255, null=False, blank=False)

    class Meta:
        verbose_name = "email bloqué"
        verbose_name_plural = "emails bloqués"

    def __str__(self):
        return f"{self.email} - {self.created}"


class BlockedDomainName(DatedModel):
    domain = models.CharField(max_length=253, verbose_name="domaine", null=False, blank=False, unique=True)
    reason = models.CharField(verbose_name="raison", max_length=255, null=False, blank=False)

    class Meta:
        verbose_name = "nom de domaine bloqué"
        verbose_name_plural = "nom de domaines bloqués"

    def __str__(self):
        return f"{self.domain} - {self.created}"
