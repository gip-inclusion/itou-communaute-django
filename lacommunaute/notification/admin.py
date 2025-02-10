from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from lacommunaute.notification.models import EmailSentTrack, Notification


@admin.register(EmailSentTrack)
class EmailSentTrackAdmin(admin.ModelAdmin):
    list_display = ("kind", "created", "status_code")
    list_filter = ("kind", "status_code")


class BaseNotificationListFilter(admin.SimpleListFilter):
    def lookups(self, request, model_admin):
        return [
            ("yes", _(self.title)),
            ("no", _("not " + self.title)),
        ]

    def queryset(self, request, queryset):
        if self.value() is not None:
            field_name = self.parameter_name + "_at"
            return queryset.filter(**{f"{field_name}__isnull": (self.value() != "yes")})


class SentNotificationListFilter(BaseNotificationListFilter):
    title = _("sent")
    parameter_name = "sent"


class VisitedNotificationListFilter(BaseNotificationListFilter):
    title = _("visited")
    parameter_name = "visited"


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ("recipient", "kind", "delay", "created", "sent_at", "visited_at", "post_id")
    list_filter = ("kind", "delay", SentNotificationListFilter, VisitedNotificationListFilter)
    raw_id_fields = ("post",)
    search_fields = ("recipient", "post__id", "post__subject")
