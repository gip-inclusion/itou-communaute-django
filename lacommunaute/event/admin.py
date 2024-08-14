from django.contrib import admin

from lacommunaute.event.models import Event


class EventAdmin(admin.ModelAdmin):
    raw_id_fields = ("poster",)
    list_display = ("name", "date", "poster")
    list_filter = ("date",)
    search_fields = ("name", "poster__email")


admin.site.register(Event, EventAdmin)
