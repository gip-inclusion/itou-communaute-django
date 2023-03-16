from django.contrib import admin

from lacommunaute.notification.models import EmailSentTrack


class EmailSentTrackAdmin(admin.ModelAdmin):
    pass


admin.site.register(EmailSentTrack, EmailSentTrackAdmin)
