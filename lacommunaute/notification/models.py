from django.db import models
from machina.models.abstract_models import DatedModel

from lacommunaute.notification.enums import EmailSentTrackKind


class EmailSentTrack(DatedModel):
    status_code = models.IntegerField(verbose_name="code de retour de l'API")
    response = models.TextField(verbose_name="réponse de l'API")
    datas = models.JSONField(verbose_name="données envoyées à l'API")
    kind = models.CharField(
        verbose_name="type", choices=EmailSentTrackKind.choices, max_length=20, null=False, blank=False
    )

    class Meta:
        verbose_name = "trace des emails envoyés"
        verbose_name_plural = "traces des emails envoyés"

    def __str__(self):
        return f"{self.status_code} - {self.created}"


class BouncedEmail(DatedModel):
    email = models.EmailField(verbose_name="email", null=False, blank=False, unique=True)
    reason = models.CharField(verbose_name="raison", max_length=255, null=False, blank=False)

    class Meta:
        verbose_name = "email bloqué"
        verbose_name_plural = "emails bloqués"

    def __str__(self):
        return f"{self.email} - {self.created}"


class BouncedDomainName(DatedModel):
    domain = models.CharField(max_length=253, verbose_name="domaine", null=False, blank=False, unique=True)
    reason = models.CharField(verbose_name="raison", max_length=255, null=False, blank=False)

    class Meta:
        verbose_name = "nom de domaine bloqué"
        verbose_name_plural = "nom de domaines bloqués"

    def __str__(self):
        return f"{self.domain} - {self.created}"
