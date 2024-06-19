from django.contrib import admin

from lacommunaute.stats.models import Stat


class StatAdmin(admin.ModelAdmin):
    list_display = ("name", "date", "value", "period")
    list_filter = ("name", "date", "period")


admin.site.register(Stat, StatAdmin)
