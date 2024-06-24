from django.contrib import admin

from lacommunaute.stats.models import ForumStat, Stat


@admin.register(Stat)
class StatAdmin(admin.ModelAdmin):
    list_display = ("name", "date", "value", "period")
    list_filter = ("name", "date", "period")


@admin.register(ForumStat)
class ForumStatAdmin(admin.ModelAdmin):
    list_display = ("date", "period", "forum", "visits", "entry_visits", "time_spent")
    list_filter = ("date", "period", "forum")
    raw_id_fields = ("forum",)
