from django.contrib import admin

from lacommunaute.notification.models import BouncedEmail, EmailSentTrack


@admin.register(EmailSentTrack)
class EmailSentTrackAdmin(admin.ModelAdmin):
    list_display = ("kind", "created", "status_code")
    list_filter = ("kind",)


@admin.register(BouncedEmail)
class BouncedEmailAdmin(admin.ModelAdmin):
    list_display = ("email", "created", "reason")
    list_filter = ("reason",)
