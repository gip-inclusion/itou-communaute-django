from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from lacommunaute.notification.models import EmailSentTrack, Notification


@admin.register(EmailSentTrack)
class EmailSentTrackAdmin(admin.ModelAdmin):
    list_display = ("kind", "created", "status_code")
    list_filter = ("kind",)


class SentNotificationListFilter(admin.SimpleListFilter):
    title = _("sent")
    parameter_name = "sent"

    def lookups(self, request, model_admin):
        return [
            ("sent", _("sent")),
            ("not sent", _("not sent")),
        ]

    def queryset(self, request, queryset):
        if self.value() is not None:
            return queryset.filter(sent_at__isnull=(self.value() != "sent"))


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ("kind", "delay", "created", "sent_at")
    list_filter = ("kind", "delay", SentNotificationListFilter)
    raw_id_fields = ("post",)
    search_fields = ("recipient", "post__id", "post__subject")
