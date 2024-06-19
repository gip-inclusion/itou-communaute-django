from django.contrib import admin

from lacommunaute.stats.models import Stat


@admin.register(Stat)
class StatAdmin(admin.ModelAdmin):
    list_display = ("name", "date", "value", "period")
    list_filter = ("name", "date", "period")
