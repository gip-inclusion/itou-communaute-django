from itertools import groupby
from operator import attrgetter

from django.db import models
from django.db.models import F
from django.utils.translation import gettext_lazy as _

from lacommunaute.notification.enums import EmailSentTrackKind, NotificationDelay
from lacommunaute.utils.abstract_models import DatedModel


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


class NotificationQuerySet(models.QuerySet):
    def group_by_recipient(self):
        return {
            recipient: list(group)
            for recipient, group in groupby(self.order_by("recipient", "kind"), key=attrgetter("recipient"))
        }

    def mark_topic_posts_read(self, topic, user):
        """
        Called when a topic's posts are read - to update the read status of associated Notification
        """
        if not topic or (not user or user.is_anonymous):
            raise ValueError()

        self.filter(
            sent_at__isnull=True, recipient=user.email, post__in=topic.posts.values_list("id", flat=True)
        ).update(sent_at=F("created"))


class Notification(DatedModel):
    recipient = models.EmailField(verbose_name=_("recipient"), null=False, blank=False)
    post = models.ForeignKey(
        "forum_conversation.Post",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="notifications",
        verbose_name=_("post"),
    )
    kind = models.CharField(
        verbose_name=_("type"), choices=EmailSentTrackKind.choices, max_length=20, null=False, blank=False
    )
    delay = models.CharField(
        verbose_name=_("delay"),
        choices=NotificationDelay.choices,
        max_length=20,
        null=False,
        blank=False,
        default=NotificationDelay.ASAP,
    )
    sent_at = models.DateTimeField(verbose_name=_("sent at"), null=True, blank=True)

    class Meta:
        verbose_name = _("Notification")
        verbose_name_plural = _("Notifications")

    def __str__(self):
        return f"{self.kind} - {self.created.strftime('%d/%m/%Y')}"

    @property
    def sent(self):
        return self.sent_at is not None

    objects = NotificationQuerySet().as_manager()
