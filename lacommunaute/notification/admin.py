from django.contrib import admin

from lacommunaute.notification.models import EmailSentTrack, TagsNotification


@admin.register(EmailSentTrack)
class EmailSentTrackAdmin(admin.ModelAdmin):
    list_display = ("kind", "created", "status_code")
    list_filter = ("kind",)


@admin.register(TagsNotification)
class NotificationsOnTagAdmin(admin.ModelAdmin):
    list_display = ("user", "digest", "newpost")
    list_filter = ("digest", "newpost")
    raw_id_fields = ("user",)
