from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class NotificationConfig(AppConfig):
    label = "notification"
    name = "lacommunaute.notification"
    verbose_name = _("Notification")
    verbose_name_plural = _("Notifications")

    def ready(self):
        from lacommunaute.forum_conversation.signals import post_create
        from lacommunaute.notification.signals import create_post_notifications

        post_create.connect(create_post_notifications)
