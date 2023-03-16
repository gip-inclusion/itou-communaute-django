from django.db import models
from machina.models.abstract_models import DatedModel


class EmailSentTrack(DatedModel):
    status_code = models.IntegerField(verbose_name="Code de retour de l'API")
    response = models.TextField(verbose_name="Réponse de l'API")
    datas = models.JSONField(verbose_name="Données envoyées à l'API")

    class Meta:
        verbose_name = "Trace des emails envoyés"
        verbose_name_plural = "Traces des emails envoyés"

    def __str__(self):
        return f"{self.status_code} - {self.created}"
