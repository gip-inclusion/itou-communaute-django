from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class NotificationConfig(AppConfig):
    label = "notification"
    name = "lacommunaute.notification"
    verbose_name = _("Notification")
    verbose_name_plural = _("Notifications")
