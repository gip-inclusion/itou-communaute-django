from django.contrib import admin

from lacommunaute.notification.models import BouncedEmail, EmailSentTrack


class EmailSentTrackAdmin(admin.ModelAdmin):
    list_display = ("kind", "created", "status_code")
    list_filter = ("kind",)


class BouncedEmailAdmin(admin.ModelAdmin):
    list_display = ("email", "created", "reason")
    list_filter = ("reason",)


admin.site.register(EmailSentTrack, EmailSentTrackAdmin)
admin.site.register(BouncedEmail, BouncedEmailAdmin)
