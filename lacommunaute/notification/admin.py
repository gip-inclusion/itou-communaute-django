from django.contrib import admin

from lacommunaute.notification.models import EmailSentTrack


class EmailSentTrackAdmin(admin.ModelAdmin):
    list_display = ("kind", "created", "status_code")
    list_filter = ("kind",)


admin.site.register(EmailSentTrack, EmailSentTrackAdmin)
