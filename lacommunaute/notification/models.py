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
