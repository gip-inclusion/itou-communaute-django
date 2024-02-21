from django.db import models
from machina.models.abstract_models import DatedModel
from taggit.managers import TaggableManager

from lacommunaute.notification.enums import EmailSentTrackKind
from lacommunaute.users.models import User


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


class TagsNotification(DatedModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    tags = TaggableManager()
    digest = models.BooleanField(verbose_name="digest", default=False)
    newpost = models.BooleanField(verbose_name="nouveau message", default=False)

    class Meta:
        verbose_name = "notification sur tag"
        verbose_name_plural = "notifications sur tags"

    def __str__(self):
        return f"{self.user.email}"
