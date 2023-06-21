from django.db import models
from machina.models.abstract_models import DatedModel

from lacommunaute.notification.enums import EmailSentTrackKind


class EmailSentTrack(DatedModel):
    status_code = models.IntegerField(verbose_name="Code de retour de l'API")
    response = models.TextField(verbose_name="Réponse de l'API")
    datas = models.JSONField(verbose_name="Données envoyées à l'API")
    kind = models.CharField(
        verbose_name="Type", choices=EmailSentTrackKind.choices, max_length=20, null=False, blank=False
    )

    class Meta:
        verbose_name = "Trace des emails envoyés"
        verbose_name_plural = "Traces des emails envoyés"

    def __str__(self):
        return f"{self.status_code} - {self.created}"


class BouncedEmail(DatedModel):
    email = models.EmailField(verbose_name="Email", null=False, blank=False, unique=True)
    reason = models.CharField(verbose_name="Raison", max_length=255, null=False, blank=False)

    class Meta:
        verbose_name = "Emails en erreur"
        verbose_name_plural = "Emails en erreur"

    def __str__(self):
        return f"{self.email} - {self.created}"
