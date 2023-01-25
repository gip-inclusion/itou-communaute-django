from django.contrib import admin

from lacommunaute.event.models import Event


class EventAdmin(admin.ModelAdmin):
    raw_id_fields = ("poster",)


admin.site.register(Event, EventAdmin)
